#!/usr/bin/env node
/**
 * Simple example demonstrating MenuStorageService usage.
 *
 * This example shows how to:
 * - Store a menu structure
 * - Retrieve the menu
 * - Get storage statistics
 */

import MenuStorageService from '../src/services/menu-storage-service.js';

async function main() {
  const menuStorage = new MenuStorageService();

  console.log('=== MenuStorageService Example ===\n');

  try {
    // Define a simple menu structure
    const menu = [
      {
        label: 'Dashboard',
        icon: 'pi pi-home',
        to: '/dashboard',
        items: [
          { label: 'Analytics', icon: 'pi pi-chart-bar', to: '/dashboard/analytics' },
          { label: 'Reports', icon: 'pi pi-file', to: '/dashboard/reports' }
        ]
      },
      {
        label: 'Settings',
        icon: 'pi pi-cog',
        to: '/settings',
        items: [
          { label: 'Profile', icon: 'pi pi-user', to: '/settings/profile' },
          { label: 'Security', icon: 'pi pi-shield', to: '/settings/security' }
        ]
      }
    ];

    // Store the menu structure
    console.log('1. Storing menu structure...');
    const itemIds = await menuStorage.storeMenuStructure(menu, 0);
    console.log(`   Stored ${itemIds.length} root menu items`);
    console.log();

    // Retrieve the menu
    console.log('2. Retrieving menu structure...');
    const retrievedMenu = await menuStorage.getMenuStructure(0);
    console.log(`   Retrieved ${retrievedMenu.length} root items`);
    console.log('   Menu structure:');
    retrievedMenu.forEach(item => {
      console.log(`   - ${item.label} (${item.items ? item.items.length : 0} subitems)`);
      if (item.items) {
        item.items.forEach(subitem => {
          console.log(`     - ${subitem.label}`);
        });
      }
    });
    console.log();

    // Get statistics
    console.log('3. Getting storage statistics...');
    const stats = await menuStorage.getStatistics();
    console.log('   Statistics:', {
      totalLinks: stats.totalLinks,
      totalFiles: stats.totalFiles,
      rootItems: stats.rootItems
    });

    console.log('\nExample completed successfully!');

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
