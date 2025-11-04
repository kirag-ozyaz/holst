import Konva from 'konva';
import { markRaw } from 'vue';
import { CanvasElement } from './CanvasElement.js';

/**
 * Класс для карточек задач
 */
export class TaskCard extends CanvasElement {
   createGroup() {
     super.createGroup();

     const rect = markRaw(new Konva.Rect({
      width: this.data.width || 300,
      height: this.data.height || 200,
      fill: 'lightblue',
      stroke: 'blue',
      strokeWidth: 2,
      cornerRadius: 5
    }));

    const text = markRaw(new Konva.Text({
      text: this.data.title || 'Untitled',
      x: 10,
      y: 10,
      fontSize: 16,
      fill: 'black',
      width: (this.data.width || 300) - 20
    }));

    if (rect && text) {
      this.group.add(rect);
      this.group.add(text);
    }

    return this.group;
  }

  getType() {
    return 'task';
  }
}