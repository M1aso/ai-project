package storage

import (
	"context"
	"fmt"
	"time"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

// Client wraps minio client for generating presigned URLs.
type Client struct {
	mc     *minio.Client
	bucket string
}

// New creates a new storage client.
func New(endpoint, key, secret, bucket string, useSSL bool) (*Client, error) {
	mc, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(key, secret, ""),
		Secure: useSSL,
	})
	if err != nil {
		return nil, err
	}
	return &Client{mc: mc, bucket: bucket}, nil
}

// PresignPut generates a presigned PUT URL for an object.
func (c *Client) PresignPut(ctx context.Context, object string, size int64, contentType string, expiry time.Duration) (string, error) {
	if size > 50*1024*1024 {
		return "", fmt.Errorf("object too large")
	}
	if contentType != "video/mp4" && contentType != "application/pdf" {
		return "", fmt.Errorf("unsupported content type")
	}
	u, err := c.mc.PresignedPutObject(ctx, c.bucket, object, expiry)
	if err != nil {
		return "", err
	}
	return u.String(), nil
}
