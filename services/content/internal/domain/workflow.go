package domain

// CanTransition checks if status can move from `from` to `to` for courses and materials.
func CanTransition(from, to string) bool {
	allowed := map[string][]string{
		"draft":     {"review"},
		"review":    {"published", "draft"},
		"published": {},
	}
	for _, v := range allowed[from] {
		if v == to {
			return true
		}
	}
	return false
}
