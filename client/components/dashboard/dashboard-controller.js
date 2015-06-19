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
 * @fileoverview DashboardCtrl is an angular controller used to initialize
 * the dashboard, fetch the dashboard's widgets configuration and expose
 * the dashboard's properties to the scope.
 * @author joemu@google.com (Joe Allan Muharsky)
 */

goog.provide('p3rf.perfkit.explorer.components.dashboard.DashboardCtrl');

goog.require('p3rf.perfkit.explorer.components.dashboard.DashboardDataService');
goog.require('p3rf.perfkit.explorer.components.dashboard.DashboardService');
goog.require('p3rf.perfkit.explorer.components.widget.WidgetFactoryService');

goog.scope(function() {
const explorer = p3rf.perfkit.explorer;
const DashboardDataService = explorer.components.dashboard.DashboardDataService;
const DashboardService = explorer.components.dashboard.DashboardService;
const WidgetFactoryService = explorer.components.widget.WidgetFactoryService;



/**
 * See module docstring for more information about purpose and usage.
 *
 * @param {!angular.Scope} $scope
 * @param {!angular.$location} $location
 * @param {DashboardDataService} dashboardDataService
 * @param {DashboardService} dashboardService
 * @param {!WidgetFactoryService} widgetFactoryService
 * @constructor
 * @ngInject
 */
explorer.components.dashboard.DashboardCtrl = function($scope, $state,
    $location, dashboardDataService, dashboardService, widgetFactoryService,
    sidebarTabService) {
  /**
   * @type {!angular.Scope}
   * @private
   */
  this.scope_ = $scope;

  /**
   * @type {!angular.$location}
   * @private
   */
  this.location_ = $location;

  this.$state_ = $state;

  /**
   * @type {DashboardDataService}
   * @private
   */
  this.dashboardDataService_ = dashboardDataService;

  /**
   * @type {!WidgetFactoryService}
   * @private
   */
  this.widgetFactoryService_ = widgetFactoryService;

  /** @export {!SidebarTabService} */
  this.tabSvc = sidebarTabService;

  /**
   * @type {DashboardService}
   * @export
   */
  this.dashboard = dashboardService;

  /**
   * Error messages raised by this controller.
   *
   * @type {Array.<string>}
   * @export
   */
  this.errors = [];

  /**
   * @type {boolean}
   * @export
   */
  this.dashboardIsLoading = false;
};
var DashboardCtrl = explorer.components.dashboard.DashboardCtrl;


/**
 * Saves the current dashboard on the server.
 * @export
 */
DashboardCtrl.prototype.saveDashboard = function() {
  this.dashboard.save();
};


});  // goog.scope
