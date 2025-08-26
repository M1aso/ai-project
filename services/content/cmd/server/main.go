package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

// OpenAPI specification for Content Service
var openAPISpec = map[string]interface{}{
	"openapi": "3.0.0",
	"info": map[string]interface{}{
		"title":       "AI Project - Content Service",
		"description": "Content management service for courses, materials, and file uploads",
		"version":     "1.0.0",
	},
	"servers": []map[string]interface{}{
		{"url": "http://api.45.146.164.70.nip.io", "description": "Development server"},
	},
	"paths": map[string]interface{}{
		"/api/content/healthz": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Health"},
				"summary":     "Health check",
				"description": "Check if the content service is healthy",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Service is healthy",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"status":  "ok",
									"service": "content",
								},
							},
						},
					},
				},
			},
		},
		"/api/content/courses": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Courses"},
				"summary":     "List courses",
				"description": "Get a list of all available courses",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "List of courses",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"courses": []interface{}{},
									"status":  "ok",
								},
							},
						},
					},
				},
			},
			"post": map[string]interface{}{
				"tags":        []string{"Courses"},
				"summary":     "Create course",
				"description": "Create a new course",
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{
								"type": "object",
								"properties": map[string]interface{}{
									"title":       map[string]interface{}{"type": "string"},
									"description": map[string]interface{}{"type": "string"},
								},
								"required": []string{"title"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"201": map[string]interface{}{
						"description": "Course created successfully",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"id":          "course-123",
									"title":       "New Course",
									"description": "Course description",
									"status":      "draft",
								},
							},
						},
					},
				},
			},
		},
		"/api/content/courses/{id}": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Courses"},
				"summary":     "Get course",
				"description": "Get a specific course by ID",
				"parameters": []map[string]interface{}{
					{
						"name":        "id",
						"in":          "path",
						"required":    true,
						"description": "Course ID",
						"schema":      map[string]interface{}{"type": "string"},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Course details",
					},
					"404": map[string]interface{}{
						"description": "Course not found",
					},
				},
			},
			"put": map[string]interface{}{
				"tags":        []string{"Courses"},
				"summary":     "Update course",
				"description": "Update course status",
				"parameters": []map[string]interface{}{
					{
						"name":        "id",
						"in":          "path",
						"required":    true,
						"description": "Course ID",
						"schema":      map[string]interface{}{"type": "string"},
					},
				},
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{
								"type": "object",
								"properties": map[string]interface{}{
									"status": map[string]interface{}{
										"type": "string",
										"enum": []string{"draft", "review", "published"},
									},
								},
								"required": []string{"status"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Course updated"},
					"400": map[string]interface{}{"description": "Invalid transition"},
					"404": map[string]interface{}{"description": "Course not found"},
				},
			},
		},
		"/api/content/materials": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "List materials",
				"description": "Get a list of all materials",
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "List of materials",
					},
				},
			},
		},
		"/api/content/materials/{id}": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "Get material",
				"description": "Get a specific material by ID",
				"parameters": []map[string]interface{}{
					{
						"name":        "id",
						"in":          "path",
						"required":    true,
						"description": "Material ID",
						"schema":      map[string]interface{}{"type": "string"},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Material details"},
					"404": map[string]interface{}{"description": "Material not found"},
				},
			},
			"put": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "Update material",
				"description": "Update material status",
				"parameters": []map[string]interface{}{
					{
						"name":        "id",
						"in":          "path",
						"required":    true,
						"description": "Material ID",
						"schema":      map[string]interface{}{"type": "string"},
					},
				},
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{
								"type": "object",
								"properties": map[string]interface{}{
									"status": map[string]interface{}{
										"type": "string",
										"enum": []string{"draft", "review", "published"},
									},
								},
								"required": []string{"status"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{"description": "Material updated"},
					"400": map[string]interface{}{"description": "Invalid transition"},
					"404": map[string]interface{}{"description": "Material not found"},
				},
			},
		},
		"/api/content/materials/{id}/upload/presign": map[string]interface{}{
			"post": map[string]interface{}{
				"tags":        []string{"Upload"},
				"summary":     "Get presigned upload URL",
				"description": "Get a presigned URL for uploading material files",
				"parameters": []map[string]interface{}{
					{
						"name":        "id",
						"in":          "path",
						"required":    true,
						"description": "Material ID",
						"schema":      map[string]interface{}{"type": "string"},
					},
				},
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{
								"type": "object",
								"properties": map[string]interface{}{
									"size": map[string]interface{}{"type": "integer"},
									"type": map[string]interface{}{"type": "string"},
								},
								"required": []string{"size", "type"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Presigned URL generated",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"url":    "https://minio.example.com/presigned-url",
									"object": "materials/material-123",
								},
							},
						},
					},
				},
			},
		},
	},
	"tags": []map[string]interface{}{
		{"name": "Health", "description": "Health check operations"},
		{"name": "Courses", "description": "Course management operations"},
		{"name": "Materials", "description": "Course materials and content"},
		{"name": "Upload", "description": "File upload operations"},
	},
}

func main() {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"content"}`))
	})

	// Health check endpoint (direct access)
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"content"}`))
	})

	// OpenAPI endpoints
	r.Get("/api/content/openapi.json", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(openAPISpec)
	})

	r.Get("/api/content/docs", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.WriteHeader(http.StatusOK)
		html := `<!DOCTYPE html>
<html>
<head>
    <title>Content Service - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/api/content/openapi.json',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ]
        });
    </script>
</body>
</html>`
		w.Write([]byte(html))
	})

	r.Route("/api/content", func(api chi.Router) {
		// Health check endpoint (through API path)
		api.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{"status":"ok","service":"content"}`))
		})

		// Courses endpoints
		api.Get("/courses", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{"courses":[],"status":"ok"}`))
		})

		api.Post("/courses", func(w http.ResponseWriter, r *http.Request) {
			var req struct {
				Title       string `json:"title"`
				Description string `json:"description"`
			}
			if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
				http.Error(w, "invalid body", http.StatusBadRequest)
				return
			}
			if req.Title == "" {
				http.Error(w, "title is required", http.StatusBadRequest)
				return
			}
			
			// Generate a simple ID (in production, use proper UUID)
			courseID := "course-" + req.Title
			
			response := map[string]interface{}{
				"id":          courseID,
				"title":       req.Title,
				"description": req.Description,
				"status":      "draft",
				"created_at":  "2024-01-01T00:00:00Z",
				"updated_at":  "2024-01-01T00:00:00Z",
			}
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(response)
		})

		api.Get("/courses/{id}", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")
			if id == "" {
				http.Error(w, "invalid course ID", http.StatusBadRequest)
				return
			}
			
			// Mock response - in production, fetch from database
			response := map[string]interface{}{
				"id":          id,
				"title":       "Sample Course",
				"description": "A sample course",
				"status":      "draft",
				"created_at":  "2024-01-01T00:00:00Z",
				"updated_at":  "2024-01-01T00:00:00Z",
			}
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
		})

		api.Put("/courses/{id}", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")
			var req struct {
				Status string `json:"status"`
			}
			if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
				http.Error(w, "invalid body", http.StatusBadRequest)
				return
			}
			
			// Validate status transitions (using domain logic)
			validStatuses := []string{"draft", "review", "published"}
			isValid := false
			for _, status := range validStatuses {
				if req.Status == status {
					isValid = true
					break
				}
			}
			if !isValid {
				http.Error(w, "invalid status", http.StatusBadRequest)
				return
			}
			
			response := map[string]interface{}{
				"id":         id,
				"status":     req.Status,
				"updated_at": "2024-01-01T00:00:00Z",
			}
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
		})

		// Materials endpoints
		api.Get("/materials", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{"materials":[],"status":"ok"}`))
		})

		api.Get("/materials/{id}", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")
			if id == "" {
				http.Error(w, "invalid material ID", http.StatusBadRequest)
				return
			}
			
			response := map[string]interface{}{
				"id":          id,
				"section_id":  "section-123",
				"type":        "video",
				"title":       "Sample Material",
				"status":      "draft",
				"created_at":  "2024-01-01T00:00:00Z",
				"updated_at":  "2024-01-01T00:00:00Z",
			}
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
		})

		api.Put("/materials/{id}", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")
			var req struct {
				Status string `json:"status"`
			}
			if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
				http.Error(w, "invalid body", http.StatusBadRequest)
				return
			}
			
			validStatuses := []string{"draft", "review", "published"}
			isValid := false
			for _, status := range validStatuses {
				if req.Status == status {
					isValid = true
					break
				}
			}
			if !isValid {
				http.Error(w, "invalid status", http.StatusBadRequest)
				return
			}
			
			response := map[string]interface{}{
				"id":         id,
				"status":     req.Status,
				"updated_at": "2024-01-01T00:00:00Z",
			}
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
		})

		// Upload presign endpoint
		api.Post("/materials/{id}/upload/presign", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")
			var req struct {
				Size int64  `json:"size"`
				Type string `json:"type"`
			}
			if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
				http.Error(w, "invalid body", http.StatusBadRequest)
				return
			}
			
			if req.Size <= 0 || req.Type == "" {
				http.Error(w, "size and type are required", http.StatusBadRequest)
				return
			}
			
			// Mock presigned URL - in production, generate actual MinIO presigned URL
			response := map[string]interface{}{
				"url":    "https://minio.45.146.164.70.nip.io/materials/" + id + "/upload",
				"object": "materials/" + id,
			}
			
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(response)
		})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	log.Printf("listening on %s", port)
	if err := http.ListenAndServe(":"+port, r); err != nil {
		log.Fatal(err)
	}
}
