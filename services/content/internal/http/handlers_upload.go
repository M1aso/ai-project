package http

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/example/content/internal/storage"
	"github.com/go-chi/chi/v5"
)

// UploadHandler manages upload presign URLs.
type UploadHandler struct {
	Storage *storage.Client
}

type presignRequest struct {
	Size int64  `json:"size"`
	Type string `json:"type"`
}

// Presign handles POST /materials/{id}/upload/presign.
func (h *UploadHandler) Presign(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var req presignRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid body", http.StatusBadRequest)
		return
	}
	object := "materials/" + id
	url, err := h.Storage.PresignPut(r.Context(), object, req.Size, req.Type, 15*time.Minute)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{"url": url, "object": object})
}
