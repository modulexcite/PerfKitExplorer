/**
 * @fileoverview Popupbox is an angular directive used to display a list of
 * elements, and maintain an "insertion element".  It's currently designed for
 * collecting column/result data in the Dashkit Explorer UI.
 *
 * Usage:
 *   <div ng-controller="DashkitQueryController">
 *     <input
 *         type="text"
 *         popupbox
 *         popupbox-data="option"
 *         popupbox-template-url="basic_popup.html">
 *     </input>
 *
 *     <script type="text/ng-template" id="basic_popup.html">
 *       <div>Popup goes here to display/modify popupbox-data.</div>
 *     </script>
 *   </div>
 *
 * @author joemu@google.com (Joe Allan Muharsky)
 */

goog.provide('p3rf.dashkit.explorer.components.popupbox.PopupboxDirective');

goog.require('goog.positioning');
goog.require('goog.positioning.Corner');
goog.require('goog.style');



goog.scope(function() {
var explorer = p3rf.dashkit.explorer;


/**
 * The Popupbox directive provides for a templated popup region that appears
 * when an element is focused, and hides the popup region when both the element
 * and the popup are de-focused.
 *
 * Attributes (prefixed by popupbox-):
 *   attr {*} template-url If provided, the URL or script ID of the template
 *     to use.
 *   scope {*} data A user-defined object that can be used in custom templates.
 *
 * @param {!angular.$timeout} $timeout Provides timeout function for deferring.
 * @return {Object} Directive definition object.
 */
explorer.components.popupbox.PopupboxDirective = function($timeout) {
  return {
    restrict: 'A',
    transclude: false,
    templateUrl: function(element, attrs) {
      return attrs['popupboxTemplateUrl'] ||
          '/static/components/popupbox/popupbox-directive.html';
    },
    scope: {
      /**
       * User-defined data that can be used in custom templates.  This can drive
       * lookups or autocomplete entries.
       */
      popupboxData: '=',

      /**
       * The model element that represents the "selected" value for the popup.
       */
      popupboxModel: '='
    },
    link: function(scope, element, attrs) {
      var input = element;
      var popup = input.children()[0];

      scope.$watch('popupboxData',
          function(newVal, oldVal) {
            if (newVal && oldVal && newVal.length == oldVal.length) { return; }
            if (goog.style.isElementShown(popup)) {
              scope.showPopup();
            }
          }, true);

      /**
       * Called when an editable row is focused.  It shows and positions the
       * popup and tracks the change in selection.
       * @param {Event} evt The event handler for the focus event.
       * @param {*} option The option that is being focused.
       */
      scope.focusInput = function(evt, option) {
        scope.showPopup();
      };

      /**
       * Called when an editable row is blurred  It hides the popup and ensures
       * that there is only one insert row (and removes blanks from the list).
       * @param {Event} evt The event handler for the blur event.
       */
      scope.blurInput = function(evt) {
        var relatedTarget = /** @type {?Node} */ (evt.relatedTarget);

        if (relatedTarget && popup &&
                goog.dom.contains(popup, relatedTarget)) {
          return;
        }

        scope.hidePopup();
      };

      /**
       * When a value is selected, sets the popupboxModel and closes the popup.
       * @param {*} value The value that should be selected.
       */
      scope.selectValue = function(value) {
        scope.popupboxModel = value;
        scope.hidePopup();
      };

      /**
       * Hides the popup.
       */
      scope.hidePopup = function() {
        if (popup) {
          goog.style.setElementShown(popup, false);
        }
      };

      /**
       * Shows the popup, relative to a specific element.
       */
      scope.showPopup = function() {
        if (popup) {
          $timeout(function() {
            goog.style.setElementShown(popup, true);

            var Overflow = goog.positioning.Overflow;
            goog.positioning.positionAtAnchor(
                input[0], goog.positioning.Corner.TOP_RIGHT,
                popup, goog.positioning.Corner.TOP_LEFT,
                null, null,
                Overflow.ADJUST_Y + Overflow.RESIZE_WIDTH);
          });
        }
      };

      /**
       * Initializes the popup, moving it to be a child of the body, and hiding
       * it.
       */
      scope.initPopup = function() {
        document.body.appendChild(popup);

        input.on('focus', function(evt) {
          scope.focusInput(evt);
        });

        popup.addEventListener('blur', scope.blurInput, true);

        input.on('blur', function(evt) {
          scope.blurInput(evt);
        });

        scope.hidePopup();
      };

      scope.initPopup();
    }
  };
};

angular.module('ui.popupbox', []).directive(
    'popupbox', ['$timeout', explorer.components.popupbox.PopupboxDirective]);

});  // goog.scope