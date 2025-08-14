package http

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/example/content/internal/db"
	"github.com/example/content/internal/domain"
	"github.com/go-chi/chi/v5"
)

// MaterialHandler manages material endpoints.
type MaterialStore interface {
	GetMaterial(ctx context.Context, id string) (db.Material, error)
}

type MaterialHandler struct {
	Repo MaterialStore
}

type updateMaterialRequest struct {
	Status string `json:"status"`
}

// Update handles PUT /materials/{id} and validates transitions.
func (h *MaterialHandler) Update(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var req updateMaterialRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid body", http.StatusBadRequest)
		return
	}
	current, err := h.Repo.GetMaterial(r.Context(), id)
	if err != nil {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	if !domain.CanTransition(current.Status, req.Status) {
		http.Error(w, "invalid transition", http.StatusBadRequest)
		return
	}
	w.WriteHeader(http.StatusOK)
}
