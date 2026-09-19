/** True if setting taskId's parent to newParentId would create a cycle. */
export function wouldCreateTaskParentCycle(taskId, newParentId, cards) {
  if (taskId === newParentId) {
    return true
  }
  if (!newParentId) {
    return false
  }
  let current = newParentId
  const byId = new Map(cards.map(c => [c.id, c]))
  while (current) {
    if (current === taskId) {
      return true
    }
    current = byId.get(current)?.parent_id || null
  }
  return false
}
