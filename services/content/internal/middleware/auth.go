package middleware

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// JWTClaims represents the JWT token claims
type JWTClaims struct {
	Sub   string   `json:"sub"`
	Roles []string `json:"roles"`
	Type  string   `json:"type"`
	jwt.RegisteredClaims
}

// contextKey is used for context values to avoid collisions
type contextKey string

const (
	UserIDKey contextKey = "user_id"
	RolesKey  contextKey = "roles"
)

// JWTAuth middleware validates JWT tokens
func JWTAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Get JWT secret from environment
		jwtSecret := os.Getenv("JWT_SECRET_KEY")
		if jwtSecret == "" {
			jwtSecret = "dev-jwt-secret-not-for-production-change-in-prod" // Default for dev
		}

		// Extract token from Authorization header
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			writeUnauthorized(w, "Authorization header required")
			return
		}

		// Check Bearer prefix
		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			writeUnauthorized(w, "Bearer token required")
			return
		}

		// Parse and validate token
		token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
			// Validate signing method
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(jwtSecret), nil
		})

		if err != nil {
			writeUnauthorized(w, "Invalid token: "+err.Error())
			return
		}

		// Validate token and extract claims
		if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
			// Check token type (should be "access")
			if claims.Type != "access" {
				writeUnauthorized(w, "Invalid token type")
				return
			}

			// Check expiration
			if claims.ExpiresAt != nil && claims.ExpiresAt.Time.Before(time.Now()) {
				writeUnauthorized(w, "Token expired")
				return
			}

			// Add user info to context
			ctx := context.WithValue(r.Context(), UserIDKey, claims.Sub)
			ctx = context.WithValue(ctx, RolesKey, claims.Roles)
			
			// Continue with the request
			next.ServeHTTP(w, r.WithContext(ctx))
		} else {
			writeUnauthorized(w, "Invalid token claims")
			return
		}
	})
}

// GetUserID extracts user ID from request context
func GetUserID(r *http.Request) string {
	if userID, ok := r.Context().Value(UserIDKey).(string); ok {
		return userID
	}
	return ""
}

// GetUserRoles extracts user roles from request context
func GetUserRoles(r *http.Request) []string {
	if roles, ok := r.Context().Value(RolesKey).([]string); ok {
		return roles
	}
	return []string{}
}

// writeUnauthorized writes a 401 Unauthorized response
func writeUnauthorized(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusUnauthorized)
	response := fmt.Sprintf(`{"detail":"%s"}`, message)
	w.Write([]byte(response))
}
