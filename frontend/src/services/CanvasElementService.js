/**
 * Сервис для управления элементами холста
 */
export class CanvasElementService {
  constructor(canvasStore) {
    this.store = canvasStore;
  }

  /**
   * Получает максимальный z_index среди всех элементов
   */
  getMaxZIndex() {
    let maxZ = 0;
    [...this.store.cards, ...this.store.notes].forEach(item => {
      if (item.z_index !== undefined && item.z_index !== null && item.z_index > maxZ) {
        maxZ = item.z_index;
      }
    });
    return maxZ;
  }

  bringToFront(elementId, elementType) {
    const maxZ = this.getMaxZIndex();
    const newZIndex = maxZ + 1;
    
    const element = elementType === 'card' 
      ? this.store.cards.find(c => c.id === elementId)
      : this.store.notes.find(n => n.id === elementId);
    
    if (element) {
      element.z_index = newZIndex;
    }
    
    return newZIndex;
  }

  /**
   * Сортирует элементы по z_index для правильного отображения
   */
  getSortedElements() {
    return [...this.store.cards, ...this.store.notes]
      .sort((a, b) => (a.z_index || 0) - (b.z_index || 0));
  }
}