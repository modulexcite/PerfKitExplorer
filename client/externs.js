/**
 * @copyright Copyright 2014 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @fileoverview Externs for Closure compiler.
 *
 * This allows us to use Angular and other things that should not be compiled,
 * while avoiding a bunch of warnings about undefined variables.
 *
 * @externs
 * @author joemu@google.com (Joe Allan Muharsky)
 */

angular.$httpBackend = function() {};
angular.$httpBackend.prototype.whenGET = function(a) {};
angular.$httpBackend.prototype.whenPOST = function(a) {};
angular.$httpBackend.prototype.passThrough = function() {};
angular.$httpBackend.prototype.respond = function(a) {};

CodeMirror.prototype.setValue = function(a) {};

function history() {}
history.pushState = function(a, b, c) {};

var CURRENT_USER_ADMIN = null;
var CURRENT_USER_EMAIL = null;
