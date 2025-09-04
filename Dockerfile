# --- Builder Stage ---
FROM golang:1.21-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the Go module files and download dependencies
# Copy the rest of the application source code
COPY app/. ./
RUN go mod download

# Build the Go application
# -o /app/mcp-server: Specifies the output binary name and location.
# CGO_ENABLED=0: Disables Cgo to produce a statically linked binary, which is important for running in a minimal container like distroless.
# -ldflags="-s -w": Strips debugging information to reduce the binary size.
RUN CGO_ENABLED=0 GOOS=linux go build -a -ldflags="-s -w" -o /app/mcp-server .

# --- Final Stage ---
FROM gcr.io/distroless/base-debian11

# Set the working directory
WORKDIR /

# Copy the built binary from the builder stage
COPY --from=builder /app/mcp-server /mcp-server

ENV LOG_LEVEL=DEBUG \
    KAKAO_API_KEY=

# Expose the port the app runs on
EXPOSE 8080

# Set the entrypoint for the container
# This command runs the application when the container starts.
ENTRYPOINT ["/mcp-server"]
