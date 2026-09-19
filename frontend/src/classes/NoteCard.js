import Konva from 'konva';
import { markRaw } from 'vue';
import { CanvasElement } from './CanvasElement.js';
import { cardThemeColors, formatCardCanvasText } from '../utils/cardDisplay.js';

/**
 * Класс для карточек заметок
 */
export class NoteCard extends CanvasElement {
   createGroup() {
     super.createGroup();

     const width = this.data.width || 250;
     const height = this.data.height || 150;
     const colors = cardThemeColors('note');

     const rect = markRaw(new Konva.Rect({
      width,
      height,
      fill: colors.fill,
      stroke: colors.stroke,
      strokeWidth: 2,
      cornerRadius: 5
    }));

     const metaText = markRaw(new Konva.Text({
      text: formatCardCanvasText('note', this.data).split('\n')[0],
      x: 10,
      y: 8,
      fontSize: 11,
      fontStyle: 'bold',
      fill: colors.metaFill,
      width: width - 20
    }));

    const titleText = markRaw(new Konva.Text({
      text: this.data.title || 'Без названия',
      x: 10,
      y: 24,
      fontSize: 14,
      fill: colors.titleFill,
      width: width - 20
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
    const colors = cardThemeColors('note');
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

  updateDisplay(data) {
    this.data = { ...this.data, ...data };
    if (this.metaText) {
      this.metaText.text(formatCardCanvasText('note', this.data).split('\n')[0]);
    }
    if (this.titleText) {
      this.titleText.text(this.data.title || 'Без названия');
    }
    this.applyTheme();
  }

  getType() {
    return 'note';
  }
}
