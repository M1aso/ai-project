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

		api.Get("/courses", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte(`{"courses":[],"status":"ok"}`))
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
