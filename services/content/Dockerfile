# Build stage
FROM golang:1.21-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/content cmd/server/main.go

# Runtime stage
FROM gcr.io/distroless/base-debian12
COPY --from=build /out/content /content
EXPOSE 8000
ENV PORT=8000
ENTRYPOINT ["/content"]
