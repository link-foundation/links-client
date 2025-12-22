/**
 * LinkDBService Tests
 *
 * Comprehensive tests for link-cli (clink) database operations wrapper
 * Issue #2271: Add tests and make LinkDB an alternative storage engine
 */

import { describe, it, before, after } from 'test-anywhere';
import assert from 'node:assert';
import LinkDBService from '../src/services/link-db-service.js';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test database path (separate from production)
const TEST_DB_DIR = path.join(__dirname, '..', 'data');
const TEST_DB_FILE = path.join(TEST_DB_DIR, 'test-linkdb.links');

// Check if clink is available (will be set in before hook)
let clinkAvailable = true;
let service;

// Helper function to conditionally skip tests at runtime
const itIfClink = (name, fn) => {
  return it(name, async function() {
    if (!clinkAvailable) {
      this.skip();
      return;
    }
    await fn.call(this);
  });
};

describe('LinkDBService', () => {
  before(async () => {
    // Ensure test data directory exists
    if (!fs.existsSync(TEST_DB_DIR)) {
      fs.mkdirSync(TEST_DB_DIR, { recursive: true });
    }

    service = new LinkDBService(TEST_DB_FILE);

    // Check if clink is available
    try {
      await service.executeQuery('(() ())', { after: true });
      clinkAvailable = true;
    } catch (error) {
      if (error.message.includes('clink command not found') || error.message.includes('LinkDB not available')) {
        clinkAvailable = false;
        console.warn('⚠️  clink not available - some tests will be skipped');
      } else {
        throw error;
      }
    }
  });

  after(async () => {
    // Clean up test database
    if (clinkAvailable) {
      try {
        await service.clearDatabase();
      } catch (error) {
        // Ignore cleanup errors
      }
    }

    // Remove test database file
    if (fs.existsSync(TEST_DB_FILE)) {
      fs.unlinkSync(TEST_DB_FILE);
    }
  });

  describe('Basic Operations', () => {
    it('should initialize with default database path', () => {
      const defaultService = new LinkDBService();
      assert.ok(defaultService.dbPath);
      assert.strictEqual(defaultService.nextId, 1);
    });

    it('should initialize with custom database path', () => {
      const customPath = '/custom/path/db.links';
      const customService = new LinkDBService(customPath);
      assert.strictEqual(customService.dbPath, customPath);
    });

    itIfClink('should execute simple query', async () => {
      const result = await service.executeQuery('(() ())', { after: true });
      assert.ok(result !== undefined);
      assert.strictEqual(typeof result, 'string');
    });

    itIfClink('should handle query with all flags', async () => {
      const result = await service.executeQuery('(() ())', {
        before: true,
        changes: true,
        after: true,
        trace: true
      });
      assert.ok(result !== undefined);
    });
  });

  describe('Link Parsing', () => {
    it('should parse empty output', () => {
      const result = service.parseLinks('');
      assert.deepStrictEqual(result, []);
    });

    it('should parse single link', () => {
      const output = '(1: 2 3)';
      const result = service.parseLinks(output);

      assert.strictEqual(result.length, 1);
      assert.deepStrictEqual(result[0], {
        id: 1,
        source: 2,
        target: 3
      });
    });

    it('should parse multiple links', () => {
      const output = `(1: 2 3)
(2: 4 5)
(3: 6 7)`;
      const result = service.parseLinks(output);

      assert.strictEqual(result.length, 3);
      assert.deepStrictEqual(result[0], { id: 1, source: 2, target: 3 });
      assert.deepStrictEqual(result[1], { id: 2, source: 4, target: 5 });
      assert.deepStrictEqual(result[2], { id: 3, source: 6, target: 7 });
    });

    it('should skip lines that do not match link pattern', () => {
      const output = `(1: 2 3)
Some random text
(2: 4 5)
Another line without pattern`;
      const result = service.parseLinks(output);

      assert.strictEqual(result.length, 2);
      assert.deepStrictEqual(result[0], { id: 1, source: 2, target: 3 });
      assert.deepStrictEqual(result[1], { id: 2, source: 4, target: 5 });
    });

    it('should handle output with extra whitespace', () => {
      const output = `

(1: 2 3)

(2: 4 5)

      `;
      const result = service.parseLinks(output);

      assert.strictEqual(result.length, 2);
    });
  });

  describe('CRUD Operations', () => {
    itIfClink('should create a link', async () => {
      const link = await service.createLink(100, 200);

      assert.ok(link);
      assert.ok(link.id > 0);
      assert.strictEqual(link.source, 100);
      assert.strictEqual(link.target, 200);
    });

    itIfClink('should read all links', async () => {
      // Create some test links
      await service.createLink(1, 2);
      await service.createLink(3, 4);
      await service.createLink(5, 6);

      const links = await service.readAllLinks();

      assert.ok(links);
      assert.ok(Array.isArray(links));
      assert.ok(links.length >= 3);
    });

    itIfClink('should read specific link by ID', async () => {
      const created = await service.createLink(10, 20);
      const linkId = created.id;

      const link = await service.readLink(linkId);

      assert.ok(link);
      assert.strictEqual(link.id, linkId);
      assert.strictEqual(link.source, 10);
      assert.strictEqual(link.target, 20);
    });

    itIfClink('should return null for non-existent link', async () => {
      const link = await service.readLink(999999);
      assert.strictEqual(link, null);
    });

    itIfClink('should update a link', async () => {
      const created = await service.createLink(10, 20);
      const linkId = created.id;

      const updated = await service.updateLink(linkId, 30, 40);

      assert.strictEqual(updated.id, linkId);
      assert.strictEqual(updated.source, 30);
      assert.strictEqual(updated.target, 40);

      // Verify the update
      const link = await service.readLink(linkId);
      assert.strictEqual(link.source, 30);
      assert.strictEqual(link.target, 40);
    });

    itIfClink('should delete a link', async () => {
      const created = await service.createLink(10, 20);
      const linkId = created.id;

      const result = await service.deleteLink(linkId);
      assert.strictEqual(result, true);

      // Verify deletion
      const link = await service.readLink(linkId);
      assert.strictEqual(link, null);
    });
  });

  describe('Menu Item Operations', () => {
    itIfClink('should store menu item', async () => {
      const menuItem = {
        label: 'Test Menu',
        icon: 'pi pi-home',
        to: '/test'
      };

      const linkId = await service.storeMenuItem(menuItem);

      assert.ok(linkId > 0);
    });

    itIfClink('should store multiple menu items', async () => {
      const items = [
        { label: 'Home', icon: 'pi pi-home', to: '/' },
        { label: 'About', icon: 'pi pi-info', to: '/about' },
        { label: 'Contact', icon: 'pi pi-envelope', to: '/contact' }
      ];

      const linkIds = [];
      for (const item of items) {
        const linkId = await service.storeMenuItem(item);
        linkIds.push(linkId);
      }

      assert.strictEqual(linkIds.length, 3);
      assert.strictEqual(new Set(linkIds).size, 3); // All IDs should be unique
    });

    itIfClink('should get all menu items', async () => {
      // Store some menu items
      await service.storeMenuItem({ label: 'Item 1', icon: 'pi-home', to: '/1' });
      await service.storeMenuItem({ label: 'Item 2', icon: 'pi-info', to: '/2' });
      await service.storeMenuItem({ label: 'Item 3', icon: 'pi-user', to: '/3' });

      const menuItems = await service.getAllMenuItems();

      assert.ok(menuItems);
      assert.ok(Array.isArray(menuItems));
      assert.ok(menuItems.length >= 3);

      // All items should have target = 1000 (menu type identifier)
      menuItems.forEach(item => {
        assert.strictEqual(item.target, 1000);
      });
    });

    itIfClink('should delete menu item', async () => {
      const linkId = await service.storeMenuItem({
        label: 'Temporary Item',
        icon: 'pi pi-trash',
        to: '/temp'
      });

      const result = await service.deleteMenuItem(linkId);
      assert.strictEqual(result, true);

      // Verify deletion
      const link = await service.readLink(linkId);
      assert.strictEqual(link, null);
    });
  });

  describe('Database Management', () => {
    itIfClink('should clear entire database', async () => {
      // Create multiple links
      await service.createLink(1, 2);
      await service.createLink(3, 4);
      await service.createLink(5, 6);

      // Verify links exist
      let links = await service.readAllLinks();
      assert.ok(links.length > 0);

      // Clear database
      const result = await service.clearDatabase();
      assert.strictEqual(result, true);

      // Verify database is empty
      links = await service.readAllLinks();
      assert.strictEqual(links.length, 0);
    });

    itIfClink('should handle clearing empty database', async () => {
      const result = await service.clearDatabase();
      assert.strictEqual(result, true);
    });
  });

  describe('Example Use Cases', () => {
    itIfClink('should handle hierarchical menu structure', async () => {
      // Clear database first
      await service.clearDatabase();

      // Create parent menu items
      const homeLink = await service.createLink(1, 0); // Root level
      const productsLink = await service.createLink(2, 0); // Root level

      // Create child menu items under "Products"
      await service.createLink(101, productsLink.id);
      await service.createLink(102, productsLink.id);

      // Verify structure
      const allLinks = await service.readAllLinks();

      // Find root items (target = 0)
      const rootItems = allLinks.filter(link => link.target === 0);
      assert.ok(rootItems.length >= 2);

      // Find children of products
      const productChildren = allLinks.filter(link => link.target === productsLink.id);
      assert.ok(productChildren.length >= 2);
    });
  });

  describe('Performance and Edge Cases', () => {
    itIfClink('should handle large numbers', async () => {
      const largeSource = 999999999;
      const largeTarget = 888888888;

      const link = await service.createLink(largeSource, largeTarget);

      assert.strictEqual(link.source, largeSource);
      assert.strictEqual(link.target, largeTarget);
    });

    itIfClink('should handle zero values', async () => {
      const link = await service.createLink(0, 0);

      assert.strictEqual(link.source, 0);
      assert.strictEqual(link.target, 0);
    });

    itIfClink('should handle rapid sequential operations', async () => {
      const operations = [];

      // Perform 10 rapid creates
      for (let i = 0; i < 10; i++) {
        operations.push(service.createLink(i, i + 100));
      }

      const results = await Promise.all(operations);

      assert.strictEqual(results.length, 10);
      results.forEach((result, index) => {
        assert.strictEqual(result.source, index);
        assert.strictEqual(result.target, index + 100);
      });
    });
  });

  describe('Error Handling', () => {
    itIfClink('should handle invalid query syntax gracefully', async () => {
      try {
        await service.executeQuery('invalid query syntax {{{{');
        // If no error is thrown, test passes (clink handles it)
      } catch (error) {
        // Error is expected and acceptable
        assert.ok(error.message.includes('LinkDB query failed'));
      }
    });
  });
});
