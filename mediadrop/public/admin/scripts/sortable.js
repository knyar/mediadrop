/**
 * This file is a part of MediaDrop (https://www.mediadrop.video),
 * Copyright 2009-2018 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * Reorder the rows of a table with drag and drop.
 *
 * Uses the browser's native drag and drop, which also scrolls the page when
 * a row is dragged to the edge of the window. Rows make way for the dragged
 * row while it is moved over them. After each drop the IDs of all rows are
 * POSTed to saveUrl in their new order, so each request saves the complete
 * order. Row IDs are taken from the id attributes, e.g. 'podcast-12' with
 * the prefix 'podcast-'.
 */
var SortableTable = new Class({

	Implements: Options,

	options: {
		saveUrl: null,
		prefix: '',
		status: null, // element to show the saving status in
		messages: {
			saving: 'Saving',
			saved: 'Saved!',
			failure: 'Saving failed. Please try again.'
		}
	},

	initialize: function(table, opts){
		this.setOptions(opts);
		this.tbody = $(table).getElement('tbody');
		this.status = $(this.options.status);
		this.dragged = null;
		this.saving = false;
		this.saveAgain = false;

		this.getRows().each(function(row){
			row.set('draggable', 'true');
			// links and images would be dragged instead of their row
			row.getElements('a, img').set('draggable', 'false');
		});
		this.tbody.addEventListener('dragstart', this.onDragStart.bind(this), false);
		this.tbody.addEventListener('dragend', this.onDragEnd.bind(this), false);
		// accept drops anywhere on the page, only a cancelled drag is undone
		document.addEventListener('dragover', this.onDragOver.bind(this), false);
		document.addEventListener('drop', this.onDrop.bind(this), false);
	},

	onDragStart: function(e){
		var row = this.getRow(e.target);
		if (!row) return;
		this.dragged = row;
		this.dropped = false;
		this.startOrder = this.serialize();
		e.dataTransfer.effectAllowed = 'move';
		// Firefox does not start dragging without data
		e.dataTransfer.setData('text', row.id);
		// highlight the row after the browser has taken its drag image
		(function(){
			if (this.dragged == row) row.addClass('dragging');
		}).delay(0, this);
	},

	onDragOver: function(e){
		if (!this.dragged) return; // not our row, e.g. a file
		e.preventDefault();
		e.dataTransfer.dropEffect = 'move';
		var row = this.getRow(e.target);
		if (!row || row == this.dragged) return;
		var box = row.getBoundingClientRect();
		var where = (e.clientY < box.top + box.height / 2) ? 'before' : 'after';
		var sibling = (where == 'before') ? row.getPrevious() : row.getNext();
		if (sibling != this.dragged) this.dragged.inject(row, where);
	},

	onDrop: function(e){
		if (!this.dragged) return;
		// stop browsers from opening the dragged text
		e.preventDefault();
		this.dropped = true;
	},

	onDragEnd: function(e){
		var row = this.dragged;
		if (!row) return;
		this.dragged = null;
		row.removeClass('dragging');
		if (!this.dropped) {
			// cancelled with the escape key or dropped outside of the window
			this.restore(this.startOrder);
		} else if (this.serialize().join(',') != this.startOrder.join(',')) {
			this.save();
		}
	},

	save: function(){
		if (this.saving) {
			// send the latest order when the current request is finished
			this.saveAgain = true;
			return;
		}
		this.saving = true;
		this.showStatus('saving');
		if (!this.request) this.request = new Request.JSON({
			url: this.options.saveUrl,
			onSuccess: function(json){ this.saved(json && json.success); }.bind(this),
			onFailure: function(){ this.saved(false); }.bind(this)
		});
		this.request.send(new Hash({ids: this.serialize()}).toQueryString());
	},

	saved: function(success){
		this.saving = false;
		if (this.saveAgain) {
			this.saveAgain = false;
			this.save();
		} else {
			this.showStatus(success ? 'saved' : 'failure');
		}
	},

	showStatus: function(state){
		if (!this.status) return;
		$clear(this.hideStatusTimer);
		var cssClass = {saving: 'form-saving', saved: 'form-saved', failure: 'form-save-error'}[state];
		this.status.empty().removeClass('hidden').adopt(
			new Element('span', {'class': cssClass, text: this.options.messages[state]})
		);
		if (state == 'saved') {
			this.hideStatusTimer = this.status.addClass.delay(2000, this.status, 'hidden');
		}
	},

	getRow: function(node){
		while (node && node.parentNode != this.tbody) node = node.parentNode;
		return $(node);
	},

	getRows: function(){
		var prefix = this.options.prefix;
		return this.tbody.getChildren().filter(function(row){
			return row.id && row.id.indexOf(prefix) == 0;
		});
	},

	serialize: function(){
		var prefix = this.options.prefix;
		return this.getRows().map(function(row){
			return row.id.substr(prefix.length);
		});
	},

	restore: function(ids){
		ids.each(function(id){
			$(this.options.prefix + id).inject(this.tbody);
		}, this);
	}

});
