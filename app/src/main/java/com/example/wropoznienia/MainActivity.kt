package com.example.wropoznienia

import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.OnMapReadyCallback
import com.google.android.gms.maps.SupportMapFragment
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.Marker
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity(), OnMapReadyCallback {
    private val REQUEST_PERMISSIONS_REQUEST_CODE = 1
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val mapFragment = supportFragmentManager.findFragmentById(R.id.map_fragment) as? SupportMapFragment
        mapFragment?.getMapAsync(this)
    }

    override fun onMapReady(googleMap: GoogleMap) {
        googleMap.moveCamera(CameraUpdateFactory.newLatLngZoom(LatLng(51.1256586, 17.006079), 12.0f))
        var vehicleMap = HashMap<String, Marker>()
        val fileDownload = FileDownload()
        val context = this

//        fileDownload.getFromFirestore(vehicleList, googleMap, db)
//
//        GlobalScope.launch {
//            while (isActive) {
//                delay(10_000)
//                runOnUiThread {
//                    vehicleList = fileDownload.updateMarkerDataOnce(vehicleList, googleMap, db)
//                }
//            }
//        }

        fileDownload.downloadFile(vehicleMap, googleMap, application, context) { updatedVehicleMap ->
            vehicleMap = updatedVehicleMap
        }

        GlobalScope.launch {
            while (isActive) {
                delay(5_000)
                runOnUiThread {
                    fileDownload.downloadFile(vehicleMap, googleMap, application, context) { updatedVehicleMap ->
                        vehicleMap = updatedVehicleMap
                    }
                }
            }
        }
    }
    public override fun onResume() {
        super.onResume()
    }

    public override fun onPause() {
        super.onPause()
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

//    private fun requestPermissionsIfNecessary(permissions: Array<String>) {
//        val permissionsToRequest = ArrayList<String>()
//        for (permission in permissions) {
//            if (ContextCompat.checkSelfPermission(this, permission)
//                != PackageManager.PERMISSION_GRANTED
//            ) {
//                // Permission is not granted
//                permissionsToRequest.add(permission)
//            }
//        }
//        if (permissionsToRequest.size > 0) {
//            ActivityCompat.requestPermissions(
//                this,
//                permissionsToRequest.toTypedArray(),
//                REQUEST_PERMISSIONS_REQUEST_CODE
//            )
//        }
//    }
}