#!/usr/bin/env node

/**
 * DaVinci Resolve MCP - Interactive Configuration Tool
 *
 * This tool provides an interactive CLI for configuring the MCP server.
 * It handles:
 * - Platform detection
 * - DaVinci Resolve path detection
 * - Client selection (Cursor, Claude, etc.)
 * - Profile selection
 * - Configuration file generation
 */

const inquirer = require('inquirer');
const chalk = require('chalk');
const ora = require('ora');
const Conf = require('conf');
const os = require('os');
const path = require('path');
const fs = require('fs').promises;
const yaml = require('js-yaml');

const config = new Conf({
  projectName: 'resolve-mcp',
  defaults: {
    platform: os.platform(),
    profile: 'full',
    proxyEnabled: false,
    maxTools: 40
  }
});

/**
 * Detect DaVinci Resolve installation paths
 */
async function detectResolvePaths() {
  const spinner = ora('Detecting DaVinci Resolve installation...').start();

  const platform = os.platform();
  let paths = {};

  try {
    switch (platform) {
      case 'darwin':
        paths = {
          apiPath: '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting',
          libPath: '/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so',
          modulesPath: '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules'
        };
        break;

      case 'win32':
        const programData = process.env.PROGRAMDATA || 'C:\\ProgramData';
        const programFiles = process.env.PROGRAMFILES || 'C:\\Program Files';
        paths = {
          apiPath: path.join(programData, 'Blackmagic Design', 'DaVinci Resolve', 'Support', 'Developer', 'Scripting'),
          libPath: path.join(programFiles, 'Blackmagic Design', 'DaVinci Resolve', 'fusionscript.dll'),
          modulesPath: path.join(programData, 'Blackmagic Design', 'DaVinci Resolve', 'Support', 'Developer', 'Scripting', 'Modules')
        };
        break;

      case 'linux':
        paths = {
          apiPath: '/opt/resolve/Developer/Scripting',
          libPath: '/opt/resolve/libs/Fusion/fusionscript.so',
          modulesPath: '/opt/resolve/Developer/Scripting/Modules'
        };
        break;

      default:
        spinner.fail(`Unsupported platform: ${platform}`);
        return null;
    }

    // Verify API path exists
    try {
      await fs.access(paths.apiPath);
      spinner.succeed('DaVinci Resolve detected');
      return paths;
    } catch (error) {
      spinner.warn('DaVinci Resolve not found at default location');

      // Ask user if they want to manually specify paths
      const { customPath } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'customPath',
          message: 'Would you like to specify custom paths?',
          default: false
        }
      ]);

      if (customPath) {
        const customPaths = await inquirer.prompt([
          {
            type: 'input',
            name: 'apiPath',
            message: 'Enter Resolve Script API path:',
            default: paths.apiPath
          },
          {
            type: 'input',
            name: 'libPath',
            message: 'Enter Resolve Script Library path:',
            default: paths.libPath
          },
          {
            type: 'input',
            name: 'modulesPath',
            message: 'Enter Resolve Modules path:',
            default: paths.modulesPath
          }
        ]);
        return customPaths;
      }

      return null;
    }
  } catch (error) {
    spinner.fail('Error detecting DaVinci Resolve');
    console.error(error);
    return null;
  }
}

/**
 * Select AI assistant client
 */
async function selectClient() {
  const answers = await inquirer.prompt([
    {
      type: 'list',
      name: 'client',
      message: 'Which AI assistant are you using?',
      choices: [
        { name: 'Cursor (VS Code-based editor)', value: 'cursor' },
        { name: 'Claude Desktop', value: 'claude' },
        { name: 'Other/Custom', value: 'custom' }
      ]
    }
  ]);

  return answers.client;
}

/**
 * Select profile configuration
 */
async function selectProfile() {
  console.log(chalk.blue('\n📋 Profile Configuration\n'));
  console.log(chalk.gray('Profiles allow you to limit which tools are exposed.'));
  console.log(chalk.gray('This is useful for Cursor (40 tool limit) and focused workflows.\n'));

  const { useProxy } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'useProxy',
      message: 'Enable tool filtering?',
      default: true
    }
  ]);

  if (!useProxy) {
    return { proxyEnabled: false, profile: 'full', maxTools: null };
  }

  const { profile } = await inquirer.prompt([
    {
      type: 'list',
      name: 'profile',
      message: 'Select tool profile:',
      choices: [
        {
          name: 'Minimal - Essential tools only (10 tools)',
          value: 'minimal',
          short: 'Minimal'
        },
        {
          name: 'Editing - Video editing workflow (35 tools)',
          value: 'editing',
          short: 'Editing'
        },
        {
          name: 'Color Grading - Color page operations (40 tools)',
          value: 'color_grading',
          short: 'Color Grading'
        },
        {
          name: 'Delivery - Rendering and export (25 tools)',
          value: 'delivery',
          short: 'Delivery'
        },
        {
          name: 'Full - All tools (requires disabling proxy)',
          value: 'full',
          short: 'Full',
          disabled: 'Enable this by disabling tool filtering'
        }
      ]
    }
  ]);

  const { maxTools } = await inquirer.prompt([
    {
      type: 'number',
      name: 'maxTools',
      message: 'Maximum tools to expose:',
      default: 40,
      validate: (value) => {
        if (value <= 0 || value > 200) {
          return 'Please enter a number between 1 and 200';
        }
        return true;
      }
    }
  ]);

  return { proxyEnabled: true, profile, maxTools };
}

/**
 * Generate MCP configuration for the selected client
 */
async function generateConfig(client, paths, proxyConfig) {
  const platform = os.platform();

  // Determine config path based on client
  let configPath;
  let configFormat = 'json'; // or 'yaml'

  switch (client) {
    case 'cursor':
      // Cursor MCP config location
      if (platform === 'win32') {
        configPath = path.join(
          process.env.APPDATA,
          'Cursor',
          'User',
          'globalStorage',
          'rooveterinaryinc.roo-cline',
          'settings',
          'cline_mcp_settings.json'
        );
      } else if (platform === 'darwin') {
        configPath = path.join(
          os.homedir(),
          'Library',
          'Application Support',
          'Cursor',
          'User',
          'globalStorage',
          'rooveterinaryinc.roo-cline',
          'settings',
          'cline_mcp_settings.json'
        );
      } else {
        configPath = path.join(
          os.homedir(),
          '.config',
          'Cursor',
          'User',
          'globalStorage',
          'rooveterinaryinc.roo-cline',
          'settings',
          'cline_mcp_settings.json'
        );
      }
      break;

    case 'claude':
      // Claude Desktop config location
      if (platform === 'win32') {
        configPath = path.join(process.env.APPDATA, 'Claude', 'claude_desktop_config.json');
      } else if (platform === 'darwin') {
        configPath = path.join(os.homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
      } else {
        configPath = path.join(os.homedir(), '.config', 'claude', 'claude_desktop_config.json');
      }
      break;

    default:
      // Custom location
      configPath = path.join(os.homedir(), '.resolve-mcp', 'mcp_config.json');
  }

  // Generate MCP server configuration
  const mcpConfig = {
    mcpServers: {
      "davinci-resolve": {
        name: "DaVinci Resolve MCP",
        command: process.platform === 'win32' ? 'resolve-mcp.cmd' : 'resolve-mcp',
        args: ['start'],
        env: {
          RESOLVE_SCRIPT_API: paths.apiPath,
          RESOLVE_SCRIPT_LIB: paths.libPath,
          PYTHONPATH: paths.modulesPath,
          RESOLVE_MCP_PROFILE: proxyConfig.profile,
          RESOLVE_MCP_PROXY: proxyConfig.proxyEnabled ? 'true' : 'false',
        }
      }
    }
  };

  // Add max_tools if specified
  if (proxyConfig.maxTools) {
    mcpConfig.mcpServers["davinci-resolve"].env.RESOLVE_MCP_MAX_TOOLS = proxyConfig.maxTools.toString();
  }

  return { configPath, mcpConfig, configFormat };
}

/**
 * Write configuration to file
 */
async function writeConfig(configPath, mcpConfig, configFormat) {
  const spinner = ora('Writing configuration...').start();

  try {
    // Ensure directory exists
    await fs.mkdir(path.dirname(configPath), { recursive: true });

    // Read existing config if it exists
    let existingConfig = {};
    try {
      const existing = await fs.readFile(configPath, 'utf8');
      if (configFormat === 'json') {
        existingConfig = JSON.parse(existing);
      } else {
        existingConfig = yaml.load(existing);
      }
    } catch (error) {
      // File doesn't exist, that's okay
    }

    // Merge configs (prefer new MCP server config)
    const finalConfig = {
      ...existingConfig,
      mcpServers: {
        ...(existingConfig.mcpServers || {}),
        ...mcpConfig.mcpServers
      }
    };

    // Write config
    let content;
    if (configFormat === 'json') {
      content = JSON.stringify(finalConfig, null, 2);
    } else {
      content = yaml.dump(finalConfig);
    }

    await fs.writeFile(configPath, content);

    spinner.succeed('Configuration saved');
    return true;
  } catch (error) {
    spinner.fail('Failed to write configuration');
    console.error(chalk.red(error.message));
    return false;
  }
}

/**
 * Save local configuration
 */
async function saveLocalConfig(paths, proxyConfig, client) {
  const configDir = path.join(os.homedir(), '.resolve-mcp');
  const configPath = path.join(configDir, 'config.yaml');

  try {
    await fs.mkdir(configDir, { recursive: true });

    const localConfig = {
      proxy_enabled: proxyConfig.proxyEnabled,
      max_tools: proxyConfig.maxTools || 40,
      active_profile: proxyConfig.profile,
      client: client,
      paths: paths,
      profiles: {
        minimal: {
          description: 'Essential tools only (10 tools)',
          categories: ['core'],
          tools: [
            'list_projects', 'open_project', 'list_timelines',
            'set_current_timeline', 'list_media_pool_clips',
            'import_media', 'add_clip_to_timeline', 'start_rendering'
          ]
        },
        editing: {
          description: 'Video editing workflow (35 tools)',
          categories: ['core', 'project', 'timeline', 'media'],
          exclude_tools: ['delete_project', 'quit_resolve_app']
        },
        color_grading: {
          description: 'Color grading workflow (40 tools)',
          categories: ['core', 'project', 'color', 'gallery', 'graph']
        },
        delivery: {
          description: 'Rendering and delivery (25 tools)',
          categories: ['core', 'project', 'delivery', 'cache']
        },
        full: {
          description: 'All tools (100+ tools)',
          categories: 'all'
        }
      }
    };

    await fs.writeFile(configPath, yaml.dump(localConfig));
    console.log(chalk.gray(`\nLocal config saved: ${configPath}`));
  } catch (error) {
    console.error(chalk.yellow('Warning: Could not save local config:'), error.message);
  }
}

/**
 * Main configuration flow
 */
async function configure() {
  console.log(chalk.blue.bold('\n🎬 DaVinci Resolve MCP Configuration Wizard\n'));

  // Step 1: Detect Resolve paths
  console.log(chalk.cyan('Step 1: Detecting DaVinci Resolve\n'));
  const paths = await detectResolvePaths();

  if (!paths) {
    console.log(chalk.yellow('\n⚠ Could not detect DaVinci Resolve installation.'));
    console.log(chalk.white('Please make sure DaVinci Resolve is installed and try again.\n'));
    process.exit(1);
  }

  // Step 2: Select client
  console.log(chalk.cyan('\nStep 2: Select AI Assistant\n'));
  const client = await selectClient();

  // Step 3: Select profile
  console.log(chalk.cyan('\nStep 3: Configure Profile\n'));
  const proxyConfig = await selectProfile();

  // Step 4: Generate and write config
  console.log(chalk.cyan('\nStep 4: Saving Configuration\n'));
  const { configPath, mcpConfig, configFormat } = await generateConfig(client, paths, proxyConfig);
  const success = await writeConfig(configPath, mcpConfig, configFormat);

  // Step 5: Save local config
  await saveLocalConfig(paths, proxyConfig, client);

  // Summary
  if (success) {
    console.log(chalk.green.bold('\n✓ Configuration Complete!\n'));

    console.log(chalk.white('Configuration Details:'));
    console.log(chalk.gray('─'.repeat(50)));
    console.log(chalk.white('  Client:'), chalk.cyan(client));
    console.log(chalk.white('  Profile:'), chalk.cyan(proxyConfig.profile));
    console.log(chalk.white('  Tool Filtering:'), chalk.cyan(proxyConfig.proxyEnabled ? 'Enabled' : 'Disabled'));

    if (proxyConfig.proxyEnabled && proxyConfig.maxTools) {
      console.log(chalk.white('  Max Tools:'), chalk.cyan(proxyConfig.maxTools));
    }

    console.log(chalk.white('  Config File:'), chalk.cyan(configPath));
    console.log(chalk.gray('─'.repeat(50)));

    console.log(chalk.yellow('\n📝 Next Steps:\n'));
    console.log(chalk.white('1.'), 'Restart your AI assistant to load the new configuration');
    console.log(chalk.white('2.'), 'Open DaVinci Resolve');
    console.log(chalk.white('3.'), 'Start using DaVinci Resolve commands in your AI assistant!');

    console.log(chalk.gray('\nUseful Commands:'));
    console.log(chalk.cyan('  resolve-mcp start'), chalk.gray('- Start the MCP server manually'));
    console.log(chalk.cyan('  resolve-mcp status'), chalk.gray('- Check server status'));
    console.log(chalk.cyan('  resolve-mcp profiles'), chalk.gray('- List available profiles'));
    console.log(chalk.cyan('  resolve-mcp use <profile>'), chalk.gray('- Switch to a different profile'));
    console.log('');
  } else {
    console.log(chalk.red('\n✗ Configuration failed\n'));
    process.exit(1);
  }

  // Save to persistent config store
  config.set('client', client);
  config.set('profile', proxyConfig.profile);
  config.set('proxyEnabled', proxyConfig.proxyEnabled);
  config.set('maxTools', proxyConfig.maxTools);
  config.set('paths', paths);
  config.set('configured', true);
  config.set('configuredAt', new Date().toISOString());
}

module.exports = configure;

// Run if called directly
if (require.main === module) {
  configure().catch((error) => {
    console.error(chalk.red('\nConfiguration error:'), error.message);
    process.exit(1);
  });
}
