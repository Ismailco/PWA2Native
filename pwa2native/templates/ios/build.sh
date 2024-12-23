#!/bin/bash

# Get the project name from the current directory
PROJECT_NAME=$(basename "$PWD")
BUILD_DIR="$(pwd)/build"

# Check if xcodebuild is available
if ! command -v xcodebuild &> /dev/null; then
    echo "Error: xcodebuild not found. Please install Xcode Command Line Tools."
    exit 1
fi

# Clean previous build
rm -rf "$BUILD_DIR"

# Build the project with development team and automatic signing
echo "Building $PROJECT_NAME for iOS..."
xcodebuild \
    -project "$PROJECT_NAME.xcodeproj" \
    -scheme "$PROJECT_NAME" \
    -configuration Debug \
    -sdk iphonesimulator \
    -destination 'platform=iOS Simulator,name=iPhone 14' \
    -derivedDataPath "$BUILD_DIR" \
    CONFIGURATION_BUILD_DIR="$BUILD_DIR/Debug-iphonesimulator" \
    CODE_SIGN_IDENTITY=- \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO \
    build

if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi

# Note: For actual device builds, you'll need:
# 1. An Apple Developer account
# 2. A valid provisioning profile
# 3. Change -sdk to iphoneos
# 4. Remove CODE_SIGN_* flags
# 5. Add -allowProvisioningUpdates
