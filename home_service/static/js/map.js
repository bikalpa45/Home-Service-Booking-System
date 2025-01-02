function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 8,
        center: {lat: 27.7172, lng: 85.3240}
    });

    const marker = new google.maps.Marker({
        map: map,
        draggable: true,
        position: {lat: 27.7172, lng: 85.3240}
    });

    google.maps.event.addListener(map, 'click', function(event) {
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();

        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;

        marker.setPosition(event.latLng);
    });

    google.maps.event.addListener(marker, 'dragend', function(event) {
        document.getElementById('latitude').value = this.getPosition().lat();
        document.getElementById('longitude').value = this.getPosition().lng();
    });
}
