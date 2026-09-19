import Konva from 'konva';
import { markRaw } from 'vue';
import { clampCardSize } from '../utils/cardDimensions.js';

/**
 * Базовый класс для всех элементов холста
 */
export class CanvasElement {
   constructor(data, canvasService, layer) {
     this.id = data.id;
     this.data = data;
     this.canvasService = canvasService;
     this.layer = layer;
     this.group = null;
   }

   /**
    * Создает визуальный элемент Konva
    */
   createGroup() {
     this.group = markRaw(new Konva.Group({
       x: this.data.x,
       y: this.data.y,
       draggable: true,
       id: this.id
     }));

     this.addEventListeners();
     return this.group;
  }

  /**
   * Добавляет общие обработчики событий
   */
  addEventListeners() {
    this.group.on('click', () => {
      this.onSelect();
    });

    this.group.on('dragstart', () => {
      this.onDragStart();
    });

    this.group.on('dragmove', () => {
      this.canvasService.requestLinksRender();
      this.canvasService.requestEditorAnchor(this.id);
    });

    this.group.on('dragend', () => {
      this.onDragEnd();
    });

    this.group.on('contextmenu', (e) => {
      e.evt.preventDefault();
      e.cancelBubble = true;
      const elementPayload = { ...this.data, type: this.getType() };
      if (this.canvasService.store.linkMode) {
        return;
      }
      const previousSelection = this.canvasService.store.selectedElement;
      this.canvasService.store.setSelectedElement(elementPayload);
      this.canvasService.requestEditorAnchor(this.id);
      if (this.canvasService.openContextMenu) {
        this.canvasService.openContextMenu(
          e.evt.clientX,
          e.evt.clientY,
          elementPayload,
          previousSelection
        );
      }
    });
  }

  /**
   * Обработчик выбора элемента
   */
  onSelect() {
    const elementPayload = { ...this.data, type: this.getType() };
    if (this.canvasService.store.linkMode) {
      this.canvasService.store.handleLinkClick(elementPayload);
      this.layer.draw();
      return;
    }
    this.canvasService.store.setSelectedElement(elementPayload);
    this.canvasService.requestEditorAnchor(this.id);
    this.bringToFront();
    this.layer.draw();
  }

  /**
   * Обработчик начала перетаскивания
   */
  onDragStart() {
    if (this.canvasService.store.linkMode) {
      return;
    }
    this.canvasService.store.setSelectedElement({ ...this.data, type: this.getType() });
    this.bringToFront();
    this.layer.draw();
  }

  /**
   * Устанавливает выделение элемента
   */
  setSelected() {
    // Сохраняем оригинальные стили
    const rect = this.group.children[0];
    if (rect && !this.originalStyles) {
      this.originalStyles = {
        stroke: rect.stroke(),
        strokeWidth: rect.strokeWidth()
      };
    }
    
    // Применяем стили выделения
    if (rect) {
      rect.stroke('red');
      rect.strokeWidth(4);
    }
  }

  /**
   * Снимает выделение элемента
   */
  removeSelection() {
    const rect = this.group.children[0];
    if (rect && this.originalStyles) {
      rect.stroke(this.originalStyles.stroke);
      rect.strokeWidth(this.originalStyles.strokeWidth);
      this.originalStyles = null;
    }
  }

  /**
   * Подсветка второго конца выбранной связи (не заменяет выделение карточки).
   */
  setLinkPeerHighlight(active) {
    const rect = this.group.children[0];
    if (!rect) return;

    if (active) {
      if (!this.peerHighlightStyles) {
        this.peerHighlightStyles = {
          stroke: rect.stroke(),
          strokeWidth: rect.strokeWidth()
        };
      }
      rect.stroke('#2563eb');
      rect.strokeWidth(3);
      return;
    }

    if (this.peerHighlightStyles) {
      if (!this.originalStyles) {
        rect.stroke(this.peerHighlightStyles.stroke);
        rect.strokeWidth(this.peerHighlightStyles.strokeWidth);
      }
      this.peerHighlightStyles = null;
    }
  }

  /**
   * Обработчик окончания перетаскивания
   */
  onDragEnd() {
    const newX = this.group.x();
    const newY = this.group.y();
    
    this.data.x = newX;
    this.data.y = newY;
    
    const newZIndex = this.bringToFront();
    this.data.z_index = newZIndex;

    const handlers = this.canvasService.positionHandlers;
    this.canvasService.requestEditorAnchor(this.id);

    if (handlers) {
      if (this.getType() === 'task') {
        handlers.updateCardPosition(this.id, newX, newY, newZIndex);
      } else {
        handlers.updateNotePosition(this.id, newX, newY, newZIndex);
      }
      return;
    }

    if (this.getType() === 'task') {
      this.canvasService.store.updateCard(this.id, { x: newX, y: newY, z_index: newZIndex });
    } else {
      this.canvasService.store.updateNote(this.id, { x: newX, y: newY, z_index: newZIndex });
    }
  }

  /**
   * Перемещает элемент на передний план
   */
  bringToFront() {
    const newZIndex = this.canvasService.bringToFront(this.id, this.getType());
    this.group.moveToTop();
    this.layer.draw();
    return newZIndex;
  }

  /**
   * Обновляет позицию элемента (только если не перетаскивается)
   */
  updateLabel(title) {
    if (typeof this.updateDisplay === 'function') {
      this.updateDisplay({ title });
      return;
    }
    if (this.group && this.group.children[1]) {
      this.group.children[1].text(title || 'Untitled');
    }
  }

  refreshTheme() {
    if (typeof this.applyTheme === 'function') {
      this.applyTheme();
    }
  }

  finalizeResizeFromTransform() {
    if (!this.group || !this.cardRect || typeof this.applySize !== 'function') {
      return null;
    }
    const scaleX = this.group.scaleX();
    const scaleY = this.group.scaleY();
    const width = this.cardRect.width() * scaleX;
    const height = this.cardRect.height() * scaleY;
    this.group.scaleX(1);
    this.group.scaleY(1);
    this.applySize(width, height);
    return clampCardSize(this.data.width, this.data.height);
  }

  updatePosition(x, y) {
    // Проверяем, не перетаскивается ли элемент
    if (this.group && !this.group.isDragging()) {
      // Обновляем позицию только если она действительно изменилась
      if (this.data.x !== x || this.data.y !== y) {
        this.data.x = x;
        this.data.y = y;
        this.group.position({ x, y });
      }
    }
  }



  /**
   * Уничтожает элемент
   */
  destroy() {
    if (this.group) {
      this.group.destroy();
    }
  }

  /**
   * Возвращает тип элемента (должен быть переопределен в наследниках)
   */
  getType() {
    throw new Error('getType() must be implemented in subclass');
  }
}