<div align="center">

```
██████╗ ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗ █████╗ ████████╗██╗██╗   ██╗███████╗
██╔══██╗██║    ██║██╔══██╗╚════██╗████╗  ██║██╔══██╗╚══██╔══╝██║██║   ██║██╔════╝
██████╔╝██║ █╗ ██║███████║ █████╔╝██╔██╗ ██║███████║   ██║   ██║██║   ██║█████╗
██╔═══╝ ██║███╗██║██╔══██║██╔═══╝ ██║╚██╗██║██╔══██║   ██║   ██║╚██╗ ██╔╝██╔══╝
██║     ╚███╔███╔╝██║  ██║███████╗██║ ╚████║██║  ██║   ██║   ██║ ╚████╔╝ ███████╗
╚═╝      ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝
```

</div>

# PWA2Native

PWA2Native is a command-line tool that converts Progressive Web Apps (PWAs) into native applications for multiple platforms. Currently under development, this tool aims to simplify the process of packaging PWAs as native apps for Android, iOS, macOS, and Windows.

⚠️ **Note:** This project is currently in development and not ready for production use.

## Features

- Convert PWAs to native applications
- Support for multiple platforms:
  - ✅ Android (using TWA - Trusted Web Activities)
  - 🚧 iOS (using WKWebView) - In development
  - ✅ macOS (using WebKit)
  - 🚧 Windows (using WebView2) - In development
- Automatic manifest fetching and parsing
- Platform-specific build configuration generation

## Prerequisites

- Python 3.6 or higher
- For Android builds:
  - Android SDK
  - Gradle
- For macOS builds:
  - Xcode Command Line Tools
  - Swift compiler

## Installation

To install PWA2Native, clone the repository and run the setup script:

```bash
git clone https://github.com/ismailco/PWA2Native.git
cd PWA2Native
```

## Usage

Basic usage:

```bash
./pwa2native.py https://example.com --name "My PWA" --platforms android,macos
```

### Arguments

- `url`: URL of the PWA (required)
- `--name`: Name of the application (default: "PWA App")
- `--platforms`: Comma-separated list of target platforms (default: "all")
  - Available options: android,ios,macos,windows
- `--output`: Output directory (default: "./dist")

### Examples

Package for all platforms:

```bash
python pwa2native.py https://my-pwa.com --name "My PWA"
```

Package only for Android:

```bash
python pwa2native.py https://my-pwa.com --name "My PWA" --platforms android
```

## Platform-Specific Build Instructions

### Android
1. Navigate to the generated Android project directory:
   ```bash
   cd dist/android
   ```
2. Build the release APK:
   ```bash
   gradle wrapper
   ./gradlew assembleRelease
   ```

### macOS
1. Navigate to the generated macOS project directory:
   ```bash
   cd dist/macos
   ```
2. Run the build script:
   ```bash
   ./build.sh
   ```

## 🤝 Contributing

We love your input! We want to make contributing to PWA2Native as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

### Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

### Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable
2. Update the CHANGELOG.md with notes on your changes
3. The PR will be merged once you have the sign-off of at least one other developer

### Any Contributions You Make Will Be Under the MIT License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

### Report Bugs Using GitHub's [Issue Tracker](https://github.com/ismailco/PWA2Native/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/ismailco/PWA2Native/issues/new); it's that easy!

### Write Bug Reports With Detail, Background, and Sample Code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### License
By contributing, you agree that your contributions will be licensed under its MIT License.

### References
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md).

## License

[MIT License](LICENSE)

## Disclaimer

This project is in active development and may contain bugs or incomplete features. Use at your own risk in production environments.

## Roadmap

- [ ] Complete iOS implementation
- [ ] Complete Windows implementation
- [ ] Add support for PWA manifest icons
- [ ] Implement digital signing for all platforms
- [ ] Add configuration file support
- [ ] Improve error handling and validation
- [ ] Create comprehensive documentation

## Support

For issues and feature requests, please use the GitHub issue tracker.

