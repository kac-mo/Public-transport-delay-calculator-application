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

    fun downloadFile(markerList: MutableList<Marker>, googleMap: GoogleMap, application: Application, context: Context): MutableList<Marker> {
        val storage = FirebaseStorage.getInstance()
        val storageRef = storage.reference.child("vehicles_data.csv")
        var markerListCopy = mutableListOf<Marker>()

        val rootPath: File = File(application.getExternalFilesDir(null), "file_test")
        if (!rootPath.exists()) {
            rootPath.mkdirs()
        }
        val localFile = File(rootPath, "vehicles_data.csv")
        // Calculate MD5 hash of the local file
        var localFileMD5 = ""
        if (localFile.exists()) {
            localFileMD5 = calculateMD5(localFile)
        }


        // Compare MD5 hashes
        compareMD5Hash(storageRef, localFileMD5) { areHashesEqual ->
            if (areHashesEqual) {
                // The file is already up to date, so directly call the reading function
                fileRead.readCsvFile(context, localFile, markerList, googleMap)

            } else {
                // Delete the old file
                if (localFile.exists()) {
                    localFile.delete()
                }

                // Download the new file
                storageRef.getFile(localFile).addOnSuccessListener {
                    Log.e("firebase ", "Local temp file created: $localFile")
                    // updateDb(timestamp, localFile.toString(), position);
                    markerListCopy = fileRead.readCsvFile(context, localFile, markerList, googleMap)
                }.addOnFailureListener { exception ->
                    Log.e("firebase ", "Local temp file not created: $exception")
                }
            }
        }
        return markerListCopy
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