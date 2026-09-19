export const CARD_MIN_WIDTH = 80
export const CARD_MIN_HEIGHT = 60

export function clampCardSize(width, height) {
  return {
    width: Math.max(CARD_MIN_WIDTH, Math.round(width || CARD_MIN_WIDTH)),
    height: Math.max(CARD_MIN_HEIGHT, Math.round(height || CARD_MIN_HEIGHT))
  }
}
