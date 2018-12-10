// https://blockchain.info/unconfirmed-transactions
// hook the following event in https://blockchain.info/Resources/unconfirmed-txs.js

window.throat = 0;

ws.onmessage = function(e) {
    console.log(e);

    var obj = $.parseJSON(e.data);

    if (obj.op == 'status') {
        $('#status').html(obj.msg);
    } else if (obj.op == 'utx') {
        op = obj.x;

        count++;

        var tx = TransactionFromJSON(op);

        _txIndexes.push(tx.txIndex);

        // -------------------------------------
        // window.throat ++;
        //
        // if ( window.throat % 1 == 0 ) {
        //     for (var i=0 ; i < tx.inputs.length ; i++)
        //         for (var j=0; j< tx.inputs.length ; j++ ) {
        //             var url = "https://localhost:8154/rest/analyze?"
        //                     + "input=" + tx.inputs[i].prev_out.addr
        //                     + "&out=" + tx.out[j].addr;
        //             $.get( url, function() { alert( "success" ); });
        //         }
        // }
        // -------------------------------------

        for (var i=0 ; i < tx.inputs.length ; i++)
            for (var j=0; j< tx.inputs.length ; j++ ) {
                console.log( tx.inputs[i].prev_out.addr + " -> " + tx.out[j].addr);
                if ( tx.inputs[i].prev_out.addr == "3CLgr137YGwgQw3fsm8Crx2Z1VxN9G6MdE"
                        && tx.out[j].addr == "16nGKDcqcRWqb3FcjTYQnsLUj3ykQbvgHT")
                        alert( "detected" );
            }

        var tx_html = tx.getHTML();

        $('#tx_container').prepend(tx_html);

        setupSymbolToggle();

        tx_html.hide().slideDown('slow');

        $('#tx_container .txdiv:last-child').remove();

        SetStatus();

        lasttx = tx;
    } else if (obj.op == 'block') {
        for (var i = 0; i < obj.x.txIndexes.length; ++i) {
            var txIndex = obj.x.txIndexes[i];

            var el = $('#tx-' + txIndex);
            if (el.length > 0) {
                el.remove();
            }

            var index = _txIndexes.indexOf(txIndex);
            if (index > -1) {
                _txIndexes.splice(index, 1);
                count--;
            }
        }

        SetStatus();

        if (sound_on) {
            playSound('ding');
        }
    } else if (obj.op == 'marker') {
        marker = new google.maps.Marker({
            map:map,
            draggable:false,
            icon: resource + 'flags/' + obj.x.cc.toLowerCase() + '.png',
            animation: google.maps.Animation.DROP,
            position: new google.maps.LatLng(obj.x.lat, obj.x.lon)
        });

        if (lasttx) {
            google.maps.event.addListener(marker, 'click', function(){ window.location.href = root + 'tx-index/' + lasttx.txIndex });
        }
    }
};
