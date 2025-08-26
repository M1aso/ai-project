package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/example/content/internal/middleware"
	"github.com/example/content/internal/service"
	"github.com/go-chi/chi/v5"
	chimiddleware "github.com/go-chi/chi/v5/middleware"
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
	"components": map[string]interface{}{
		"securitySchemes": map[string]interface{}{
			"BearerAuth": map[string]interface{}{
				"type":   "http",
				"scheme": "bearer",
				"bearerFormat": "JWT",
			},
		},
	},
	"security": []map[string]interface{}{
		{"BearerAuth": []string{}},
	},
	"paths": map[string]interface{}{
		"/api/content/healthz": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Health"},
				"summary":     "Health check",
				"description": "Check if the content service is healthy",
				"security":    []map[string]interface{}{}, // No auth required
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
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "List of courses",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"courses": []map[string]interface{}{
										{
											"id":          "course-example",
											"title":       "Example Course",
											"description": "An example course",
											"status":      "published",
											"created_at":  "2024-01-01T00:00:00Z",
											"updated_at":  "2024-01-01T00:00:00Z",
										},
									},
									"status": "ok",
								},
							},
						},
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"detail": "Not authenticated",
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
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{
								"type": "object",
								"properties": map[string]interface{}{
									"title":       map[string]interface{}{"type": "string"},
									"description": map[string]interface{}{"type": "string"},
									"category":    map[string]interface{}{"type": "string"},
								},
								"required": []string{"title", "description"},
							},
							"example": map[string]interface{}{
								"title":       "New Course",
								"description": "Course description",
								"category":    "technology",
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
									"id":          "course-new-course",
									"title":       "New Course",
									"description": "Course description",
									"status":      "draft",
									"created_at":  "2024-01-01T00:00:00Z",
									"updated_at":  "2024-01-01T00:00:00Z",
								},
							},
						},
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
				},
			},
		},
		"/api/content/courses/{id}": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Courses"},
				"summary":     "Get course",
				"description": "Get a specific course by ID",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
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
						"content": map[string]interface{}{
							"application/json": map[string]interface{}{
								"example": map[string]interface{}{
									"id":          "course-example",
									"title":       "Example Course",
									"description": "An example course",
									"status":      "published",
									"created_at":  "2024-01-01T00:00:00Z",
									"updated_at":  "2024-01-01T00:00:00Z",
								},
							},
						},
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
					"404": map[string]interface{}{
						"description": "Course not found",
					},
				},
			},
			"put": map[string]interface{}{
				"tags":        []string{"Courses"},
				"summary":     "Update course",
				"description": "Update a course status",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
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
										"enum": []string{"draft", "published", "archived"},
									},
								},
								"required": []string{"status"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Course updated successfully",
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
					"404": map[string]interface{}{
						"description": "Course not found",
					},
				},
			},
		},
		"/api/content/materials": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "List materials",
				"description": "Get a list of all materials",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "List of materials",
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
				},
			},
			"post": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "Create material",
				"description": "Create a new learning material",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
				"requestBody": map[string]interface{}{
					"required": true,
					"content": map[string]interface{}{
						"application/json": map[string]interface{}{
							"schema": map[string]interface{}{
								"type": "object",
								"properties": map[string]interface{}{
									"section_id": map[string]interface{}{"type": "string"},
									"type":       map[string]interface{}{"type": "string"},
									"title":      map[string]interface{}{"type": "string"},
								},
								"required": []string{"section_id", "type", "title"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"201": map[string]interface{}{
						"description": "Material created successfully",
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
				},
			},
		},
		"/api/content/materials/{id}": map[string]interface{}{
			"get": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "Get material",
				"description": "Get a specific material by ID",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
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
					"200": map[string]interface{}{
						"description": "Material details",
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
					"404": map[string]interface{}{
						"description": "Material not found",
					},
				},
			},
			"put": map[string]interface{}{
				"tags":        []string{"Materials"},
				"summary":     "Update material",
				"description": "Update a material status",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
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
										"enum": []string{"draft", "published", "archived"},
									},
								},
								"required": []string{"status"},
							},
						},
					},
				},
				"responses": map[string]interface{}{
					"200": map[string]interface{}{
						"description": "Material updated successfully",
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
					"404": map[string]interface{}{
						"description": "Material not found",
					},
				},
			},
		},
		"/api/content/materials/{id}/upload/presign": map[string]interface{}{
			"post": map[string]interface{}{
				"tags":        []string{"Upload"},
				"summary":     "Get upload presign URL",
				"description": "Get a presigned URL for uploading material content",
				"security":    []map[string]interface{}{{"BearerAuth": []string{}}},
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
									"upload_url": "https://minio.minio.svc.cluster.local:9000/materials/material-123.mp4",
									"asset_url":  "https://minio.minio.svc.cluster.local:9000/materials/material-123.mp4",
								},
							},
						},
					},
					"401": map[string]interface{}{
						"description": "Not authenticated",
					},
				},
			},
		},
	},
	"tags": []map[string]interface{}{
		{"name": "Health", "description": "Health check operations"},
		{"name": "Courses", "description": "Course management operations"},
		{"name": "Materials", "description": "Learning material operations"},
		{"name": "Upload", "description": "File upload operations"},
	},
}

func main() {
	// Get database URL from environment
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		log.Fatal("DATABASE_URL environment variable is required")
	}

	// Initialize content service with database connection
	contentService, err := service.NewContentService(databaseURL)
	if err != nil {
		log.Fatalf("Failed to initialize content service: %v", err)
	}
	defer contentService.Close()

	r := chi.NewRouter()
	r.Use(chimiddleware.Logger)
	r.Use(chimiddleware.Recoverer)
	r.Use(chimiddleware.SetHeader("Content-Type", "application/json"))

	// Health check endpoint (no auth required)
	r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"content"}`))
	})

	// API routes with JWT authentication
	r.Route("/api/content", func(api chi.Router) {
		// Public endpoints (no auth required)
		api.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{"status":"ok","service":"content"}`))
		})

		api.Get("/openapi.json", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(openAPISpec)
		})

		api.Get("/docs", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "text/html")
			w.WriteHeader(http.StatusOK)
			html := `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Content Service API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/content/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [ SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset ],
                plugins: [ SwaggerUIBundle.plugins.DownloadUrl ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>`
			w.Write([]byte(html))
		})

		// Protected endpoints (JWT auth required)
		api.Group(func(protected chi.Router) {
			protected.Use(middleware.JWTAuth)

			// Course endpoints
			protected.Get("/courses", func(w http.ResponseWriter, r *http.Request) {
				courses, err := contentService.GetCourses()
				if err != nil {
					http.Error(w, `{"error":"Failed to retrieve courses"}`, http.StatusInternalServerError)
					return
				}

				response := map[string]interface{}{
					"courses": courses,
					"status":  "ok",
				}
				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(response)
			})

			protected.Post("/courses", func(w http.ResponseWriter, r *http.Request) {
				var req struct {
					Title       string `json:"title"`
					Description string `json:"description"`
					Category    string `json:"category"`
				}
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
					return
				}

				if req.Title == "" || req.Description == "" {
					http.Error(w, `{"error":"Title and description are required"}`, http.StatusBadRequest)
					return
				}

				course, err := contentService.CreateCourse(req.Title, req.Description, req.Category)
				if err != nil {
					http.Error(w, `{"error":"Failed to create course"}`, http.StatusInternalServerError)
					return
				}

				w.WriteHeader(http.StatusCreated)
				json.NewEncoder(w).Encode(course)
			})

			protected.Get("/courses/{id}", func(w http.ResponseWriter, r *http.Request) {
				id := chi.URLParam(r, "id")
				if id == "" {
					http.Error(w, `{"error":"Course ID is required"}`, http.StatusBadRequest)
					return
				}

				course, err := contentService.GetCourse(id)
				if err != nil {
					if err.Error() == "course not found" {
						http.Error(w, `{"error":"Course not found"}`, http.StatusNotFound)
						return
					}
					http.Error(w, `{"error":"Failed to retrieve course"}`, http.StatusInternalServerError)
					return
				}

				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(course)
			})

			protected.Put("/courses/{id}", func(w http.ResponseWriter, r *http.Request) {
				id := chi.URLParam(r, "id")
				var req struct {
					Status string `json:"status"`
				}
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
					return
				}

				if req.Status == "" {
					http.Error(w, `{"error":"Status is required"}`, http.StatusBadRequest)
					return
				}

				course, err := contentService.UpdateCourse(id, req.Status)
				if err != nil {
					if err.Error() == "course not found" {
						http.Error(w, `{"error":"Course not found"}`, http.StatusNotFound)
						return
					}
					http.Error(w, `{"error":"Failed to update course"}`, http.StatusInternalServerError)
					return
				}

				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(course)
			})

			// Material endpoints
			protected.Get("/materials", func(w http.ResponseWriter, r *http.Request) {
				materials, err := contentService.GetMaterials()
				if err != nil {
					http.Error(w, `{"error":"Failed to retrieve materials"}`, http.StatusInternalServerError)
					return
				}

				response := map[string]interface{}{
					"materials": materials,
					"status":    "ok",
				}
				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(response)
			})

			protected.Post("/materials", func(w http.ResponseWriter, r *http.Request) {
				var req struct {
					SectionID string `json:"section_id"`
					Type      string `json:"type"`
					Title     string `json:"title"`
				}
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
					return
				}

				if req.SectionID == "" || req.Type == "" || req.Title == "" {
					http.Error(w, `{"error":"section_id, type, and title are required"}`, http.StatusBadRequest)
					return
				}

				material, err := contentService.CreateMaterial(req.SectionID, req.Type, req.Title)
				if err != nil {
					http.Error(w, `{"error":"Failed to create material"}`, http.StatusInternalServerError)
					return
				}

				w.WriteHeader(http.StatusCreated)
				json.NewEncoder(w).Encode(material)
			})

			protected.Get("/materials/{id}", func(w http.ResponseWriter, r *http.Request) {
				id := chi.URLParam(r, "id")
				if id == "" {
					http.Error(w, `{"error":"Material ID is required"}`, http.StatusBadRequest)
					return
				}

				material, err := contentService.GetMaterial(id)
				if err != nil {
					if err.Error() == "material not found" {
						http.Error(w, `{"error":"Material not found"}`, http.StatusNotFound)
						return
					}
					http.Error(w, `{"error":"Failed to retrieve material"}`, http.StatusInternalServerError)
					return
				}

				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(material)
			})

			protected.Put("/materials/{id}", func(w http.ResponseWriter, r *http.Request) {
				id := chi.URLParam(r, "id")
				var req struct {
					Status string `json:"status"`
				}
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
					return
				}

				if req.Status == "" {
					http.Error(w, `{"error":"Status is required"}`, http.StatusBadRequest)
					return
				}

				material, err := contentService.UpdateMaterial(id, req.Status)
				if err != nil {
					if err.Error() == "material not found" {
						http.Error(w, `{"error":"Material not found"}`, http.StatusNotFound)
						return
					}
					http.Error(w, `{"error":"Failed to update material"}`, http.StatusInternalServerError)
					return
				}

				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(material)
			})

			// Upload presign endpoint
			protected.Post("/materials/{id}/upload/presign", func(w http.ResponseWriter, r *http.Request) {
				id := chi.URLParam(r, "id")
				var req struct {
					Size int64  `json:"size"`
					Type string `json:"type"`
				}
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
					return
				}

				if req.Size <= 0 || req.Type == "" {
					http.Error(w, `{"error":"Size and type are required"}`, http.StatusBadRequest)
					return
				}

				// Generate presigned URL (mock implementation)
				response := map[string]interface{}{
					"upload_url": "https://minio.minio.svc.cluster.local:9000/materials/" + id + ".mp4",
					"asset_url":  "https://minio.minio.svc.cluster.local:9000/materials/" + id + ".mp4",
				}

				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(response)
			})

			// Media assets endpoint for content-worker (internal API)
			protected.Patch("/media-assets/{id}", func(w http.ResponseWriter, r *http.Request) {
				id := chi.URLParam(r, "id")
				var req struct {
					Status     string            `json:"status"`
					Error      string            `json:"error,omitempty"`
					Renditions map[string]string `json:"renditions,omitempty"`
				}
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
					return
				}

				if req.Status == "" {
					http.Error(w, `{"error":"Status is required"}`, http.StatusBadRequest)
					return
				}

				// Log the asset update (in real implementation, this would update database)
				log.Printf("Asset %s status updated to: %s", id, req.Status)
				if req.Error != "" {
					log.Printf("Asset %s error: %s", id, req.Error)
				}
				if len(req.Renditions) > 0 {
					log.Printf("Asset %s renditions: %+v", id, req.Renditions)
				}

				response := map[string]interface{}{
					"id":     id,
					"status": req.Status,
				}
				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(response)
			})
		})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	log.Printf("Content service starting on port %s", port)
	log.Printf("Database URL: %s", databaseURL)
	log.Fatal(http.ListenAndServe(":"+port, r))
}