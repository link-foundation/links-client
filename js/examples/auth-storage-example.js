#!/usr/bin/env node
/**
 * Simple example demonstrating AuthStorageService usage.
 *
 * This example shows how to:
 * - Create a user
 * - Set a password
 * - Create an API token
 * - Retrieve user information
 */

import AuthStorageService from '../src/services/AuthStorageService.js';

async function main() {
  const authStorage = new AuthStorageService();

  console.log('=== AuthStorageService Example ===\n');

  try {
    // Create a user
    console.log('1. Creating a user...');
    const user = await authStorage.createUser({
      username: 'alice',
      email: 'alice@example.com',
      profile: {
        firstName: 'Alice',
        lastName: 'Smith'
      }
    });
    console.log('   Created user:', {
      userId: user.userId,
      username: user.username,
      email: user.email
    });
    console.log();

    // Set password
    console.log('2. Setting password for user...');
    const password = await authStorage.setPassword(user.userId, {
      hash: 'hashed_password_here',
      salt: 'random_salt_here',
      algorithm: 'pbkdf2-sha512',
      iterations: 100000
    });
    console.log('   Password set with ID:', password.passwordId);
    console.log();

    // Create an API token
    console.log('3. Creating an API token...');
    const token = await authStorage.createToken(user.userId, {
      apiKey: 'api_key_12345',
      permissions: ['read', 'write'],
      description: 'Example token'
    });
    console.log('   Created token:', {
      tokenId: token.tokenId,
      apiKey: token.apiKey,
      permissions: token.permissions
    });
    console.log();

    // Retrieve user
    console.log('4. Retrieving user information...');
    const retrievedUser = await authStorage.getUser(user.userId);
    console.log('   Retrieved user:', retrievedUser.username);
    console.log();

    // Get statistics
    console.log('5. Getting storage statistics...');
    const stats = await authStorage.getStatistics();
    console.log('   Statistics:', {
      totalUsers: stats.users.files,
      totalTokens: stats.tokens.files,
      totalPasswords: stats.passwords.files
    });

    console.log('\nExample completed successfully!');

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
