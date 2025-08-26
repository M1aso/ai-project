package middleware

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

// Claims represents JWT claims structure
type Claims struct {
	Sub   string   `json:"sub"`   // User ID
	Roles []string `json:"roles"` // User roles
	Type  string   `json:"type"`  // Token type
	jwt.RegisteredClaims
}

// JWTAuth middleware for validating JWT tokens
func JWTAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Skip authentication for health checks and docs
		if r.URL.Path == "/healthz" || 
		   r.URL.Path == "/api/content/healthz" || 
		   r.URL.Path == "/api/content/openapi.json" || 
		   r.URL.Path == "/api/content/docs" {
			next.ServeHTTP(w, r)
			return
		}

		// Get Authorization header
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, `{"detail":"Not authenticated"}`, http.StatusUnauthorized)
			return
		}

		// Check Bearer token format
		if !strings.HasPrefix(authHeader, "Bearer ") {
			http.Error(w, `{"detail":"Invalid token format"}`, http.StatusUnauthorized)
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")

		// Parse and validate JWT token
		token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
			// Validate signing method
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}

			// Get JWT secret from environment
			jwtSecret := os.Getenv("JWT_SECRET_KEY")
			if jwtSecret == "" {
				jwtSecret = "dev-jwt-secret-not-for-production-change-in-prod" // Default for dev
			}
			return []byte(jwtSecret), nil
		})

		if err != nil {
			http.Error(w, `{"detail":"Invalid token"}`, http.StatusUnauthorized)
			return
		}

		// Validate token and extract claims
		if claims, ok := token.Claims.(*Claims); ok && token.Valid {
			// Add user info to request context
			ctx := context.WithValue(r.Context(), "user_id", claims.Sub)
			ctx = context.WithValue(ctx, "user_roles", claims.Roles)
			next.ServeHTTP(w, r.WithContext(ctx))
		} else {
			http.Error(w, `{"detail":"Invalid token claims"}`, http.StatusUnauthorized)
			return
		}
	})
}

// GetUserID extracts user ID from request context
func GetUserID(r *http.Request) string {
	if userID, ok := r.Context().Value("user_id").(string); ok {
		return userID
	}
	return ""
}

// GetUserRoles extracts user roles from request context
func GetUserRoles(r *http.Request) []string {
	if roles, ok := r.Context().Value("user_roles").([]string); ok {
		return roles
	}
	return []string{}
}