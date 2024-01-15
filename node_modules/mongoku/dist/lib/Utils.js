"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var Utils;
(function (Utils) {
    /**
     * In-place sort of the given array of objects
     * @param arr An array of objects
     * @param field the field used to sort
     * @param descending whether to use descending order
     */
    Utils.fieldSort = (arr, field, descending = false) => {
        return arr.sort((a, b) => {
            return (a[field] == b[field])
                ? 0
                : (a[field] > b[field])
                    ? (descending) ? -1 : 1
                    : (descending) ? 1 : -1;
        });
    };
})(Utils = exports.Utils || (exports.Utils = {}));
