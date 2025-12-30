//! Logger utilities for the Links Client library

use tracing::Level;
use tracing_subscriber::FmtSubscriber;

/// Initialize the logger with default settings
///
/// This sets up a tracing subscriber with INFO level logging.
/// Call this at the start of your application to enable logging.
pub fn init_logger() {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();

    tracing::subscriber::set_global_default(subscriber).expect("setting default subscriber failed");
}

/// Initialize the logger with debug level logging
pub fn init_debug_logger() {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::DEBUG)
        .finish();

    tracing::subscriber::set_global_default(subscriber).expect("setting default subscriber failed");
}
