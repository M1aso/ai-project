package http

import "net/http"

// AssetHandler handles asset lifecycle operations.
type AssetHandler struct{}

// Finalize marks upload as ready.
func (h *AssetHandler) Finalize(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNoContent)
}
