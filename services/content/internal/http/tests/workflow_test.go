package tests

import (
	"bytes"
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/example/content/internal/db"
	api "github.com/example/content/internal/http"
	"github.com/go-chi/chi/v5"
)

type stubRepo struct{}

func (stubRepo) GetCourse(_ context.Context, id string) (db.Course, error) {
	return db.Course{ID: id, Status: "published"}, nil
}

func (stubRepo) GetMaterial(_ context.Context, id string) (db.Material, error) {
	return db.Material{ID: id, Status: "published"}, nil
}

func TestCourseUpdateInvalidTransition(t *testing.T) {
	h := api.CourseHandler{Repo: stubRepo{}}
	r := chi.NewRouter()
	r.Put("/courses/{id}", h.Update)
	req := httptest.NewRequest(http.MethodPut, "/courses/c1", bytes.NewBufferString(`{"status":"draft"}`))
	rr := httptest.NewRecorder()
	r.ServeHTTP(rr, req)
	if rr.Code != http.StatusBadRequest {
		t.Fatalf("expected 400 got %d", rr.Code)
	}
}
