import Konva from 'konva';
import { markRaw } from 'vue';
import { CanvasElement } from './CanvasElement.js';
import { cardThemeColors, formatCardCanvasText } from '../utils/cardDisplay.js';
import { clampCardSize } from '../utils/cardDimensions.js';

/**
 * Класс для карточек задач
 */
export class TaskCard extends CanvasElement {
   createGroup() {
     super.createGroup();

     const { width, height } = clampCardSize(this.data.width, this.data.height);
     this.data.width = width;
     this.data.height = height;
     const colors = cardThemeColors('task');

     const rect = markRaw(new Konva.Rect({
      name: 'cardRect',
      width,
      height,
      fill: colors.fill,
      stroke: colors.stroke,
      strokeWidth: 2,
      cornerRadius: 5
    }));

     const metaText = markRaw(new Konva.Text({
      name: 'metaText',
      text: formatCardCanvasText('task', this.data).split('\n')[0],
      x: 10,
      y: 8,
      fontSize: 11,
      fontStyle: 'bold',
      fill: colors.metaFill,
      width: width - 20,
      ellipsis: true,
      wrap: 'none'
    }));

    const titleText = markRaw(new Konva.Text({
      name: 'titleText',
      text: this.data.title || 'Без названия',
      x: 10,
      y: 26,
      fontSize: 16,
      fill: colors.titleFill,
      width: width - 20,
      height: Math.max(20, height - 36),
      ellipsis: true,
      wrap: 'word'
    }));

    if (rect && metaText && titleText) {
      this.group.add(rect);
      this.group.add(metaText);
      this.group.add(titleText);
      this.metaText = metaText;
      this.titleText = titleText;
      this.cardRect = rect;
    }

    return this.group;
  }

  applyTheme() {
    const colors = cardThemeColors('task');
    if (this.cardRect) {
      this.cardRect.fill(colors.fill);
      this.cardRect.stroke(colors.stroke);
    }
    if (this.metaText) {
      this.metaText.fill(colors.metaFill);
    }
    if (this.titleText) {
      this.titleText.fill(colors.titleFill);
    }
  }

  applySize(width, height) {
    const size = clampCardSize(width, height);
    this.data.width = size.width;
    this.data.height = size.height;
    if (!this.cardRect) {
      return;
    }
    this.cardRect.width(size.width);
    this.cardRect.height(size.height);
    const inner = size.width - 20;
    if (this.metaText) {
      this.metaText.width(inner);
    }
    if (this.titleText) {
      this.titleText.width(inner);
      this.titleText.height(Math.max(20, size.height - 36));
    }
  }

  updateDisplay(data) {
    this.data = { ...this.data, ...data };
    if (data.width != null || data.height != null) {
      this.applySize(this.data.width, this.data.height);
    }
    if (this.metaText) {
      this.metaText.text(formatCardCanvasText('task', this.data).split('\n')[0]);
    }
    if (this.titleText) {
      this.titleText.text(this.data.title || 'Без названия');
    }
    this.applyTheme();
  }

  getType() {
    return 'task';
  }
}
