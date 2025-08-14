package http

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/example/content/internal/db"
	"github.com/example/content/internal/domain"
	"github.com/go-chi/chi/v5"
)

// CourseHandler manages course endpoints.
type CourseStore interface {
	GetCourse(ctx context.Context, id string) (db.Course, error)
}

type CourseHandler struct {
	Repo CourseStore
}

type updateCourseRequest struct {
	Status string `json:"status"`
}

// Update handles PUT /courses/{id} and validates status transitions.
func (h *CourseHandler) Update(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	var req updateCourseRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid body", http.StatusBadRequest)
		return
	}
	current, err := h.Repo.GetCourse(r.Context(), id)
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
