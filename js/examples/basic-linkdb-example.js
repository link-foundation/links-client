#!/usr/bin/env node
/**
 * Simple example demonstrating basic LinkDB operations.
 *
 * This example shows how to:
 * - Create links between entities
 * - Read links from the database
 * - Update existing links
 * - Delete links
 */

import LinkDBService from '../src/services/LinkDBService.js';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  // Create a LinkDB service with a temporary database
  const dbPath = path.join(__dirname, 'example.links');
  const linkdb = new LinkDBService(dbPath);

  console.log('=== Basic LinkDB Example ===\n');

  try {
    // Create a link between two entities
    console.log('1. Creating a link between entity 100 and entity 200...');
    const link = await linkdb.createLink(100, 200);
    console.log(`   Created link:`, link);
    console.log();

    // Create another link
    console.log('2. Creating another link between entity 300 and entity 400...');
    const link2 = await linkdb.createLink(300, 400);
    console.log(`   Created link:`, link2);
    console.log();

    // Read all links
    console.log('3. Reading all links from the database...');
    const allLinks = await linkdb.readAllLinks();
    console.log(`   Found ${allLinks.length} links:`);
    allLinks.forEach(link => {
      console.log(`   - Link ${link.id}: ${link.source} -> ${link.target}`);
    });
    console.log();

    // Update a link
    console.log('4. Updating the first link to point to entity 500...');
    const updatedLink = await linkdb.updateLink(link.id, 100, 500);
    console.log(`   Updated link:`, updatedLink);
    console.log();

    // Delete a link
    console.log('5. Deleting the second link...');
    await linkdb.deleteLink(link2.id);
    console.log('   Link deleted');
    console.log();

    // Verify final state
    console.log('6. Final state of the database:');
    const finalLinks = await linkdb.readAllLinks();
    console.log(`   Total links: ${finalLinks.length}`);
    finalLinks.forEach(link => {
      console.log(`   - Link ${link.id}: ${link.source} -> ${link.target}`);
    });

    // Cleanup
    console.log('\nCleaning up example database...');
    await fs.unlink(dbPath).catch(() => {});
    console.log('Done!');

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
