#!/bin/bash
swiftc main.swift \
    -target x86_64-apple-macosx10.15 \
    -sdk $(xcrun --show-sdk-path) \
    -framework Cocoa \
    -framework WebKit \
    -o "${app_name}.app/Contents/MacOS/${app_name}"
