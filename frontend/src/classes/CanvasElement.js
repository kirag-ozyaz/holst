import Konva from 'konva';
import { markRaw } from 'vue';

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

    this.group.on('dragend', () => {
      this.onDragEnd();
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
   * Обработчик окончания перетаскивания
   */
  onDragEnd() {
    const newX = this.group.x();
    const newY = this.group.y();
    
    this.data.x = newX;
    this.data.y = newY;
    
    const newZIndex = this.bringToFront();
    this.data.z_index = newZIndex;
    
    // Сохраняем позицию
    if (this.layer.parent) {
      // Через Canvas.vue методы
      if (this.getType() === 'task') {
        this.layer.parent.updateCardPosition(this.id, newX, newY, newZIndex);
      } else {
        this.layer.parent.updateNotePosition(this.id, newX, newY, newZIndex);
      }
    } else {
      // Прямо через store
      if (this.getType() === 'task') {
        this.canvasService.store.updateCard(this.id, { x: newX, y: newY, z_index: newZIndex });
      } else {
        this.canvasService.store.updateNote(this.id, { x: newX, y: newY, z_index: newZIndex });
      }
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
    if (this.group && this.group.children[1]) {
      this.group.children[1].text(title || 'Untitled');
    }
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