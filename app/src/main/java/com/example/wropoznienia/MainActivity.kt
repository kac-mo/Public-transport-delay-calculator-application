package com.example.wropoznienia

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.preference.PreferenceManager
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.opencsv.CSVReader
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import org.apache.commons.lang3.mutable.Mutable
import org.osmdroid.api.IMapController
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import java.io.InputStreamReader


class MainActivity : AppCompatActivity() {
    private val REQUEST_PERMISSIONS_REQUEST_CODE = 1
    private var map: MapView? = null
    public override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        //handle permissions first, before map is created. not depicted here

        //load/initialize the osmdroid configuration, this can be done
        val ctx = applicationContext
        Configuration.getInstance().load(ctx, PreferenceManager.getDefaultSharedPreferences(ctx))
        //setting this before the layout is inflated is a good idea
        //it 'should' ensure that the map has a writable location for the map cache, even without permissions
        //if no tiles are displayed, you can try overriding the cache path using Configuration.getInstance().setCachePath
        //see also StorageUtils
        //note, the load method also sets the HTTP User Agent to your application's package name, abusing osm's
        //tile servers will get you banned based on this string

        //inflate and create the map
        setContentView(R.layout.activity_main)
        map = findViewById<View>(R.id.map) as MapView
        map!!.setTileSource(TileSourceFactory.MAPNIK)
        requestPermissionsIfNecessary(
            arrayOf( // if you need to show the current location, uncomment the line below
                Manifest.permission.ACCESS_FINE_LOCATION,
                // WRITE_EXTERNAL_STORAGE is required in order to show the map
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
        )
        map!!.setBuiltInZoomControls(true);
        map!!.setMultiTouchControls(true);
        val mapController = map!!.controller
        mapController.setZoom(14)
        val startPoint = GeoPoint(51.10190, 16.99834)
        mapController.setCenter(startPoint)
        var stopList = mutableListOf<Marker>()
        var vehicleList = mutableListOf<Marker>()
        map!!.setMinZoomLevel(12.0)
        map!!.setMaxZoomLevel(18.0)

        stopList = readCsvFile(R.raw.stops, stopList)
        vehicleList = readCsvFile(R.raw.vehicles_data, vehicleList)

        GlobalScope.launch {
            while (isActive) {
                if (map!!.zoomLevel < 14) {
                    for(stop in stopList) {
                        map!!.overlays.remove(stop)
                    }
                    stopList.clear()
                    map!!.invalidate()
                } else {
                    if (stopList.isEmpty()) {
                        stopList = readCsvFile(R.raw.stops, stopList)
                    }
                    map!!.invalidate()
                }
            }
        }
    }

    public override fun onResume() {
        super.onResume()
        //this will refresh the osmdroid configuration on resuming.
        //if you make changes to the configuration, use
        //SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
        //Configuration.getInstance().load(this, PreferenceManager.getDefaultSharedPreferences(this));
        map!!.onResume() //needed for compass, my location overlays, v6.0.0 and up
    }

    public override fun onPause() {
        super.onPause()
        //this will refresh the osmdroid configuration on resuming.
        //if you make changes to the configuration, use
        //SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
        //Configuration.getInstance().save(this, prefs);
        map!!.onPause() //needed for compass, my location overlays, v6.0.0 and up
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        val permissionsToRequest = ArrayList<String>()
        for (i in grantResults.indices) {
            permissionsToRequest.add(permissions[i])
        }
        if (permissionsToRequest.size > 0) {
            ActivityCompat.requestPermissions(
                this,
                permissionsToRequest.toTypedArray(),
                REQUEST_PERMISSIONS_REQUEST_CODE
            )
        }
    }


    private fun readCsvFile(file: Int, markerList: MutableList<Marker>): MutableList<Marker> {
        var markerListCopy = markerList
        var csvLines = ""
        try {
            val reader = CSVReader(InputStreamReader(resources.openRawResource(file))) // Specify asset file name
            var nextLine: Array<String>?
            nextLine = reader.readNext();
            if (nextLine[1] == "route_id") {
                while (reader.readNext().also { nextLine = it } != null) {
                    // nextLine[] is an array of values from the line
                    csvLines = nextLine!!.joinToString(separator = ",")
                    markerListCopy = addVehicleToMap(createVehicleObject(csvLines), markerListCopy)
                }
            } else {
                while (reader.readNext().also { nextLine = it } != null) {
                    // nextLine[] is an array of values from the line
                    csvLines = nextLine!!.joinToString(separator = ",")
                    markerListCopy = addStopToMap(createStopObject(csvLines), markerListCopy)
                }
            }
            reader.close()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "The specified file was not found", Toast.LENGTH_SHORT).show()
        }
        return markerListCopy
    }

    private fun createVehicleObject(mpkLine: String): Vehicle {
        val values = mpkLine.split(",")
        return Vehicle(
            values[0].toInt(),
            values[1],
            values[2],
            values[3].toDouble(),
            values[4].toDouble()
        )
    }

    private fun createStopObject(mpkLine: String): Stop {
        val values = mpkLine.split(",")
        return Stop(
            values[0].toInt(),
            values[1].toInt(),
            values[2],
            values[3].toDouble(),
            values[4].toDouble()
        )
    }

    private fun addStopToMap(stop: Stop, stopList: MutableList<Marker>): MutableList<Marker> {
        val stopMarker = Marker(map)
        stopMarker.position = GeoPoint(stop.positionLat, stop.positionLon)
        stopMarker.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
        map!!.overlays.add(stopMarker)
        stopMarker.setIcon(getResources().getDrawable(R.drawable.mymarker3));
        stopMarker.setTitle(stop.name);
        stopList.add(stopMarker)
        return stopList
    }

    private fun addVehicleToMap(vehicle: Vehicle, vehicleList: MutableList<Marker>): MutableList<Marker> {
        val vehicleMarker = Marker(map)
        vehicleMarker.position = GeoPoint(vehicle.positionLat, vehicle.positionLon)
        vehicleMarker.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
        map!!.overlays.add(vehicleMarker)
        vehicleMarker.setIcon(getResources().getDrawable(R.drawable.mymarker));
        vehicleMarker.setTitle("Szczur nr " + vehicle.routeId + "\nKierunek: " + vehicle.direction);
        vehicleList.add(vehicleMarker)
        return vehicleList
    }

    private fun requestPermissionsIfNecessary(permissions: Array<String>) {
        val permissionsToRequest = ArrayList<String>()
        for (permission in permissions) {
            if (ContextCompat.checkSelfPermission(this, permission)
                != PackageManager.PERMISSION_GRANTED
            ) {
                // Permission is not granted
                permissionsToRequest.add(permission)
            }
        }
        if (permissionsToRequest.size > 0) {
            ActivityCompat.requestPermissions(
                this,
                permissionsToRequest.toTypedArray(),
                REQUEST_PERMISSIONS_REQUEST_CODE
            )
        }
    }
}