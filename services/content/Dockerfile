# Build stage
FROM golang:1.21-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 go build -o /out/content cmd/server/main.go
RUN CGO_ENABLED=0 go build -o /out/migrate cmd/migrate/main.go

# Runtime stage
FROM gcr.io/distroless/base-debian12
COPY --from=build /out/content /content
COPY --from=build /out/migrate /migrate
COPY --from=build /src/internal/db/migrations /internal/db/migrations
EXPOSE 8000
ENV PORT=8000
ENTRYPOINT ["/content"]
