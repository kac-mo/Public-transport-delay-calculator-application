package com.example.wropoznienia

import android.app.Application
import android.content.Context
import android.util.Log
import androidx.core.content.FileProvider
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.Marker
import com.google.android.gms.maps.model.MarkerOptions
import com.google.firebase.crashlytics.buildtools.reloc.org.apache.commons.io.output.ByteArrayOutputStream
import com.google.firebase.firestore.DocumentSnapshot
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.storage.FirebaseStorage
import com.google.firebase.storage.StorageReference
import java.io.File
import java.io.FileInputStream
import java.security.MessageDigest

class FileDownload {

    private val fileRead = FileRead()

    fun downloadFile(
        vehicleMap: HashMap<String, Marker>,
        googleMap: GoogleMap,
        application: Application,
        context: Context,
        callback: (HashMap<String, Marker>) -> Unit
    ): HashMap<String, Marker> {
        val storage = FirebaseStorage.getInstance()
        val storageRef = storage.reference.child("vehicles_data.csv")
        val vehicleMapCopy = HashMap<String, Marker>()
        vehicleMapCopy.putAll(vehicleMap)
        for ((key, value) in vehicleMapCopy) {
            Log.d("HashMapPrint1", "Key: $key, Value: $value")
        }

        val rootPath: File = File(application.getExternalFilesDir(null), "file_test")
        if (!rootPath.exists()) {
            rootPath.mkdirs()
        }
        val localFile = File(rootPath, "vehicles_data.csv")
        if (localFile.exists()) {
            localFile.delete()
        }
        storageRef.getFile(localFile).addOnSuccessListener {
            Log.e("firebase ", "Local temp file created: $localFile")
            fileRead.readCsvFile(context, localFile, vehicleMapCopy, googleMap) { vehicleMapCopy ->
                if (vehicleMapCopy.isEmpty()) {
                    Log.d("HashMapPrint", "First check")
                }
                // Invoke the callback with the updated map
                callback(vehicleMapCopy)
            }
        }.addOnFailureListener { exception ->
            Log.e("firebase ", "Local temp file not created: $exception")
            // Handle the failure case if needed
            // For example, you can call the callback with the original vehicleMapCopy
            callback(vehicleMapCopy)
        }

        if (vehicleMapCopy.isEmpty()) {
            Log.d("HashMapPrint", "Second check")
        }
        return vehicleMapCopy
    }



//    fun getFromFirestore(markerList: MutableList<Marker>, googleMap: GoogleMap, db: FirebaseFirestore) {
//        val collectionRef = db.collection("mpkdata")
//        collectionRef.get()
//            .addOnSuccessListener { result ->
//                for (document in result) {
//                    val uniqueId = document.getString("unique_id")
//                    val latitude = document.getDouble("position_lat")
//                    val longitude = document.getDouble("position_lon")
//                    val routeId = document.getString("route_id")
//                    val direction = document.getString("direction")
//                    val transportMpkPosition = LatLng(latitude!!, longitude!!)
//                    val markerName: Marker = googleMap.addMarker(
//                        MarkerOptions()
//                            .position(transportMpkPosition)
//                            .title("Szczur - linia " + routeId)
//                            .icon(BitmapDescriptorFactory.fromResource(R.drawable.mymarker))
//                            .snippet("Kierunek: " + direction))
////                    markerName.tag = uniqueId
//                    markerName.tag = document.id
//                    markerList.add(markerName)
//
//                }
//            }
//            .addOnFailureListener { e: Exception ->
//                Log.e("firebase ", "Problem :(", e)
//            }
//    }
//
//    fun updateMarkerData(markerList: MutableList<Marker>, googleMap: GoogleMap, db: FirebaseFirestore) {
//        for (marker in markerList) {
//            val docRef = db.collection("mpkdata").document(marker.tag.toString())
//            docRef.get()
//                .addOnSuccessListener { document ->
//                    if (document != null) {
//                        val latitude = document.getDouble("position_lat")
//                        val longitude = document.getDouble("position_lon")
//                        if (latitude != null && longitude != null) {
//                            val transportMpkPosition = LatLng(latitude, longitude)
//                            marker.setPosition(transportMpkPosition)
//                        } else {
//                            markerList.remove(marker)
//                        }
//
//
//                    } else {
//                        markerList.remove(marker)
//                    }
//                }
//                .addOnFailureListener { e: Exception ->
//                    Log.e("firebase ", "Problem :(", e)
//                }
//
//        }
//    }
//
//    fun updateMarkerDataOnce(markerList: MutableList<Marker>, googleMap: GoogleMap, db: FirebaseFirestore): MutableList<Marker> {
//        val markerListCopy = mutableListOf<Marker>()
//
//        val collectionRef = db.collection("mpkdata")
//        collectionRef.get()
//            .addOnSuccessListener { result ->
//                val documentMap = mutableMapOf<String, DocumentSnapshot>()
//                for (document in result) {
//                    if (document != null) {
//                        documentMap[document.id] = document
//                    }
//                }
//
//                for (marker in markerList) {
//                    val documentId = marker.tag // Assuming marker.id corresponds to document ID
//                    val document = documentMap[documentId]
//                    if (document != null) {
//                        val latitude = document.getDouble("position_lat")
//                        val longitude = document.getDouble("position_lon")
//                        if (latitude != null && longitude != null) {
//                            val transportMpkPosition = LatLng(latitude, longitude)
//                            marker.setPosition(transportMpkPosition)
//                            markerListCopy.add(marker)
//                        }
//                    }
//                }
//            }
//            .addOnFailureListener { e: Exception ->
//                Log.e("firebase", "Problem :(", e)
//            }
//
//        return markerListCopy
//    }

}