/**
 * Test file to verify CI/CD error detection system
 *
 * This file intentionally contains ESLint errors that should be:
 * 1. Detected by the CI/CD pipeline
 * 2. Captured in error logs
 * 3. Auto-fixed by the auto-fix-linter workflow
 * 4. Commented on the PR by comment-on-failure workflow
 */

// ESLint error: unused variable
const unusedVariable = 'This should be removed';

// ESLint error: console.log in production code
console.log('This is a test');

// ESLint error: var instead of const/let
var oldStyleVariable = 'Should use const or let';

// ESLint error: missing semicolon (if configured)
const missingSemicolon = 'test'

// ESLint error: unused import (if configured)
import { useState, useEffect } from 'react';

export function testCicdErrorDetection() {
  // ESLint error: prefer arrow function
  const myFunction = function() {
    return 'test';
  };

  // ESLint error: unnecessary return
  if (true) {
    return myFunction();
  } else {
    return 'default';
  }
}

// ESLint error: default export not allowed (if configured)
export default testCicdErrorDetection;
