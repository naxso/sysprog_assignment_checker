# Base image with Rust
FROM rust:latest

# Set working directory
WORKDIR /submission

# Copy the entire submission
COPY . /submission

# Compile the Rust code (if needed)
RUN cargo build --release

# Default command to run the compiled binary
CMD ["cargo", "run", "--release"]