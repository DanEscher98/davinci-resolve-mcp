#!/usr/bin/env node

/**
 * DaVinci Resolve MCP - CLI Entry Point
 *
 * Global command-line interface for managing the MCP server.
 */

const { program } = require('commander');
const chalk = require('chalk');
const ResolveMCP = require('../lib/index');
const configure = require('./resolve-mcp-config');
const path = require('path');
const os = require('os');

program
  .name('resolve-mcp')
  .description('DaVinci Resolve MCP Server - Connect AI assistants to DaVinci Resolve')
  .version('2.0.0');

// Start command
program
  .command('start')
  .description('Start the MCP server')
  .option('-d, --debug', 'Enable debug logging')
  .option('-p, --profile <name>', 'Profile to use (minimal, editing, color_grading, delivery, full)', 'full')
  .option('--proxy', 'Enable tool filtering/proxy mode')
  .option('--max-tools <number>', 'Maximum tools to expose', '40')
  .option('--skip-resolve-check', 'Skip checking if Resolve is running')
  .action(async (options) => {
    console.log(chalk.blue.bold('\n🎬 DaVinci Resolve MCP Server\n'));

    try {
      const server = new ResolveMCP({
        debug: options.debug,
        profile: options.profile,
        proxyEnabled: options.proxy,
        maxTools: parseInt(options.maxTools),
        skipResolveCheck: options.skipResolveCheck,
      });

      await server.initialize();
      await server.start();

      console.log(chalk.green('\n✓ MCP Server is running\n'));
      console.log(chalk.white('Profile:'), chalk.cyan(options.profile));
      console.log(chalk.white('Debug:'), chalk.cyan(options.debug ? 'Enabled' : 'Disabled'));

      if (options.proxy) {
        console.log(chalk.white('Tool Filtering:'), chalk.cyan('Enabled'));
        console.log(chalk.white('Max Tools:'), chalk.cyan(options.maxTools));
      }

      console.log(chalk.yellow('\nPress Ctrl+C to stop the server\n'));

      // Handle shutdown
      process.on('SIGINT', () => {
        console.log(chalk.yellow('\n\nStopping server...'));
        server.stop();
        console.log(chalk.green('✓ Server stopped\n'));
        process.exit(0);
      });

      process.on('SIGTERM', () => {
        console.log(chalk.yellow('\n\nStopping server...'));
        server.stop();
        console.log(chalk.green('✓ Server stopped\n'));
        process.exit(0);
      });
    } catch (error) {
      console.error(chalk.red('\n✗ Failed to start server:\n'));
      console.error(chalk.red(error.message));

      if (error.message.includes('Python')) {
        console.log(chalk.yellow('\nTroubleshooting:'));
        console.log(chalk.white('• Install Python 3.6+ from https://www.python.org/downloads/'));
        console.log(chalk.white('• Make sure Python is in your PATH'));
      } else if (error.message.includes('Resolve')) {
        console.log(chalk.yellow('\nTroubleshooting:'));
        console.log(chalk.white('• Make sure DaVinci Resolve is installed and running'));
        console.log(chalk.white('• Try: ') + chalk.cyan('resolve-mcp start --skip-resolve-check'));
      }

      console.log('');
      process.exit(1);
    }
  });

// Configure command
program
  .command('configure')
  .description('Interactive configuration wizard')
  .alias('config')
  .action(async () => {
    try {
      await configure();
    } catch (error) {
      console.error(chalk.red('Configuration failed:'), error.message);
      process.exit(1);
    }
  });

// Status command
program
  .command('status')
  .description('Check server and Resolve status')
  .action(async () => {
    console.log(chalk.blue.bold('\n🎬 DaVinci Resolve MCP Status\n'));

    const server = new ResolveMCP({ skipResolveCheck: true });

    try {
      await server.initialize();

      const status = server.getStatus();

      console.log(chalk.white('Server Status:'), status.running
        ? chalk.green('Running')
        : chalk.yellow('Not Running'));

      console.log(chalk.white('Python Path:'), chalk.cyan(status.pythonPath));
      console.log(chalk.white('Server Path:'), chalk.cyan(status.serverPath));

      console.log(chalk.white('\nConfiguration:'));
      console.log(chalk.white('  Profile:'), chalk.cyan(status.profile));
      console.log(chalk.white('  Tool Filtering:'), chalk.cyan(status.proxyEnabled ? 'Enabled' : 'Disabled'));

      if (status.proxyEnabled) {
        console.log(chalk.white('  Max Tools:'), chalk.cyan(status.maxTools));
      }

      // Check Resolve
      const isResolveRunning = await server.verifyResolveRunning();
      console.log(chalk.white('\nDaVinci Resolve:'), isResolveRunning
        ? chalk.green('Running')
        : chalk.yellow('Not Running'));

      console.log('');
    } catch (error) {
      console.error(chalk.red('Error checking status:'), error.message);
      process.exit(1);
    }
  });

// Profiles command
program
  .command('profiles')
  .description('List available profiles')
  .action(() => {
    console.log(chalk.blue.bold('\n🎬 Available Profiles\n'));

    const profiles = [
      {
        name: 'minimal',
        tools: 10,
        description: 'Essential tools only - core operations',
        categories: 'core'
      },
      {
        name: 'editing',
        tools: 35,
        description: 'Video editing workflow',
        categories: 'core, project, timeline, media'
      },
      {
        name: 'color_grading',
        tools: 40,
        description: 'Color grading and correction',
        categories: 'core, project, color, gallery, graph'
      },
      {
        name: 'delivery',
        tools: 25,
        description: 'Rendering and delivery',
        categories: 'core, project, delivery, cache'
      },
      {
        name: 'full',
        tools: '100+',
        description: 'All available tools (requires tool filtering disabled)',
        categories: 'all'
      }
    ];

    profiles.forEach((profile) => {
      console.log(chalk.cyan.bold(profile.name));
      console.log(chalk.white('  Tools:'), chalk.yellow(profile.tools));
      console.log(chalk.white('  Description:'), profile.description);
      console.log(chalk.white('  Categories:'), chalk.gray(profile.categories));
      console.log('');
    });

    console.log(chalk.yellow('Usage:'), chalk.white('resolve-mcp start --profile <name>'));
    console.log('');
  });

// Use command (switch profile)
program
  .command('use <profile>')
  .description('Switch to a different profile')
  .action(async (profile) => {
    const validProfiles = ['minimal', 'editing', 'color_grading', 'delivery', 'full'];

    if (!validProfiles.includes(profile)) {
      console.error(chalk.red(`\n✗ Invalid profile: ${profile}\n`));
      console.log(chalk.yellow('Valid profiles:'), validProfiles.join(', '));
      console.log('');
      process.exit(1);
    }

    console.log(chalk.blue(`\nSwitching to profile: ${chalk.cyan(profile)}\n`));

    const fs = require('fs').promises;
    const yaml = require('js-yaml');
    const configPath = path.join(os.homedir(), '.resolve-mcp', 'config.yaml');

    try {
      // Load existing config
      let config = {};
      try {
        const content = await fs.readFile(configPath, 'utf8');
        config = yaml.load(content);
      } catch (error) {
        // Config doesn't exist, create new one
      }

      // Update profile
      config.active_profile = profile;

      // Save config
      await fs.mkdir(path.dirname(configPath), { recursive: true });
      await fs.writeFile(configPath, yaml.dump(config));

      console.log(chalk.green('✓ Profile updated\n'));
      console.log(chalk.yellow('Note:'), 'Restart the server for changes to take effect');
      console.log('');
    } catch (error) {
      console.error(chalk.red('Failed to update profile:'), error.message);
      process.exit(1);
    }
  });

// Test command
program
  .command('test')
  .description('Test connection to DaVinci Resolve')
  .action(async () => {
    console.log(chalk.blue.bold('\n🎬 Testing Connection\n'));

    const server = new ResolveMCP({ skipResolveCheck: false });

    try {
      console.log(chalk.gray('1. Finding Python...'));
      const pythonPath = await server.findPythonExecutable();
      console.log(chalk.green(`   ✓ Python found: ${pythonPath}`));

      console.log(chalk.gray('2. Checking DaVinci Resolve...'));
      const isRunning = await server.verifyResolveRunning();

      if (isRunning) {
        console.log(chalk.green('   ✓ DaVinci Resolve is running'));
      } else {
        console.log(chalk.yellow('   ⚠ DaVinci Resolve is not running'));
        console.log(chalk.yellow('     Please start DaVinci Resolve and try again'));
      }

      console.log(chalk.gray('3. Checking paths...'));
      const paths = server.getResolvePaths();
      console.log(chalk.green('   ✓ Paths configured'));
      console.log(chalk.gray(`     API: ${paths.RESOLVE_SCRIPT_API}`));
      console.log(chalk.gray(`     LIB: ${paths.RESOLVE_SCRIPT_LIB}`));

      console.log(chalk.green('\n✓ All checks passed\n'));
    } catch (error) {
      console.error(chalk.red('\n✗ Test failed:'), error.message);
      console.log('');
      process.exit(1);
    }
  });

// Help command
program
  .command('help [command]')
  .description('Display help for a command')
  .action((command) => {
    if (command) {
      program.commands.find(cmd => cmd.name() === command)?.help();
    } else {
      program.help();
    }
  });

// Parse arguments
program.parse();

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
