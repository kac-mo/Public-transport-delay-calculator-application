package com.example.wropoznienia

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Environment
import android.preference.PreferenceManager
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.firebase.crashlytics.buildtools.reloc.org.apache.commons.codec.digest.DigestUtils
import com.google.firebase.crashlytics.buildtools.reloc.org.apache.commons.io.output.ByteArrayOutputStream
import com.google.firebase.ktx.Firebase
import com.google.firebase.storage.FirebaseStorage
import com.google.firebase.storage.StorageReference
import com.google.firebase.storage.ktx.storage
import com.opencsv.CSVReader
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import java.io.File
import java.io.FileInputStream
import java.io.FileNotFoundException
import java.io.InputStreamReader
import java.security.MessageDigest


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

        //var storage = Firebase.storage
        //var storageRef = storage.reference

        //val gsReference = storage.getReferenceFromUrl("gs://wropoznienia-a3395.appspot.com/vehicles_data.csv")
        //val file = gsReference.getStream();

        downloadFile(vehicleList)

        //stopList = readCsvFile(R.raw.stops, stopList)
        //vehicleList = readCsvFile("/storage/emulated/0/Android/data/com.example.wropoznienia/files/file_test/vehicles_data.csv", vehicleList)

        /***
        GlobalScope.launch {
            while (isActive) {
                delay(30_000)
                /***
                if (map!!.zoomLevel < 14) {
                    for(stop in stopList) {
                        map!!.overlays.remove(stop)
                    }
                    stopList.clear()
                    map!!.invalidate()
                } else {
                    if (stopList.isEmpty()) {
                        //stopList = readCsvFile(R.raw.stops, stopList)
                    }
                    map!!.invalidate()
                }
                ***/
                for (vehicle in vehicleList) {
                    map!!.overlays.remove(vehicle)
                }
                vehicleList.clear()
                map!!.invalidate()
                downloadFile(vehicleList)
            }
        }
        ***/
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

    private fun calculateMD5(file: File): String {
        val digest = MessageDigest.getInstance("MD5")
        val buffer = ByteArray(8192)
        val inputStream = FileInputStream(file)
        var read: Int
        while (inputStream.read(buffer).also { read = it } > 0) {
            digest.update(buffer, 0, read)
        }
        inputStream.close()

        val md5sum = digest.digest()
        val hexString = StringBuilder()
        for (i in md5sum.indices) {
            val hex = Integer.toHexString(0xFF and md5sum[i].toInt())
            if (hex.length == 1) {
                hexString.append('0')
            }
            hexString.append(hex)
        }
        return hexString.toString()
    }
    private fun downloadFile(markerList: MutableList<Marker>) {
        val storage = FirebaseStorage.getInstance()
        val storageRef = storage.reference.child("vehicles_data.csv")

        val rootPath: File = File(application.getExternalFilesDir(null), "file_test")
        if (!rootPath.exists()) {
            rootPath.mkdirs()
        }
        val localFile = File(rootPath, "vehicles_data.csv")

        // Calculate MD5 hash of the local file
        val localFileMD5 = calculateMD5(localFile)

        // Compare MD5 hashes
        compareMD5Hash(storageRef, localFileMD5) { areHashesEqual ->
            if (areHashesEqual) {
                // The file is already up to date, so directly call the reading function
                readCsvFile(localFile, markerList)
            } else {
                // Delete the old file
                if (localFile.exists()) {
                    localFile.delete()
                }

                // Download the new file
                storageRef.getFile(localFile).addOnSuccessListener {
                    Log.e("firebase ", "Local temp file created: $localFile")
                    // updateDb(timestamp, localFile.toString(), position);
                    readCsvFile(localFile, markerList)
                }.addOnFailureListener { exception ->
                    Log.e("firebase ", "Local temp file not created: $exception")
                }
            }
        }
    }


    private fun compareMD5Hash(storageRef: StorageReference, localFileMD5: String, callback: (Boolean) -> Unit) {
        val stream = ByteArrayOutputStream()
        storageRef.metadata.addOnSuccessListener { metadata ->
            val remoteMD5Hash = metadata.md5Hash
            val areHashesEqual = remoteMD5Hash.equals(localFileMD5, ignoreCase = true)
            stream.close()
            callback(areHashesEqual)
        }.addOnFailureListener {
            stream.close()
            callback(false)
        }
    }




    private fun readCsvFile(file: File, markerList: MutableList<Marker>): MutableList<Marker> {
        var markerListCopy = markerList
        var csvLines = ""
        try {
            val fileInputStream = FileInputStream(file)
            val reader = CSVReader(InputStreamReader(fileInputStream))
            var nextLine: Array<String>?
            nextLine = reader.readNext()
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
            fileInputStream.close()
        } catch (e: FileNotFoundException) {
            e.printStackTrace()
            Toast.makeText(this, "The specified file was not found", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Different error, mabye can't add rat?", Toast.LENGTH_SHORT).show()
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