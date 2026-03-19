"use strict";

/**
 * @typedef {object} CompileProfile
 * @property {string} ext
 * @property {string} compiler
 * @property {string} flags
 */

/**
 * @typedef {object} MakefileConfigEntry
 * @property {string} output_makefile
 * @property {CompileProfile[]} compile_profiles
 * @property {string} link_compiler
 * @property {string} link_flags
 * @property {string} run_args
 * @property {string} bin_name
 * @property {string[]} rel_sources
 * @property {string} obj_expr
 */

module.exports = {};
