package com.example.wropoznienia

import android.content.Context
import android.widget.Toast
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.Marker
import com.google.android.gms.maps.model.MarkerOptions
import com.opencsv.CSVReader
import java.io.*


class FileRead {

    fun readCsvFile(
        context: Context, // Added Context parameter
        file: File,
        markerList: MutableList<Marker>,
        googleMap: GoogleMap
    ): MutableList<Marker> {
        var markerListCopy = mutableListOf<Marker>()
        markerListCopy.addAll(markerList)
        var csvLines = ""
        try {
            val fileInputStream = FileInputStream(file)
            val reader = CSVReader(InputStreamReader(fileInputStream))
            var nextLine: Array<String>?
            nextLine = reader.readNext()
            while (reader.readNext().also { nextLine = it } != null) {
                // nextLine[] is an array of values from the line
                csvLines = nextLine!!.joinToString(separator = ",")
                try {
                    markerListCopy = addVehicleToMap(markerListCopy, csvLines, googleMap)
                } catch (e: Exception) {
                    e.printStackTrace()
                    Toast.makeText(context, "Different error, maybe can't add rat?", Toast.LENGTH_SHORT).show()
                }
            }

            reader.close()
            fileInputStream.close()
        } catch (e: FileNotFoundException) {
            e.printStackTrace()
            Toast.makeText(context, "The specified file was not found", Toast.LENGTH_SHORT).show()
        }
        return markerListCopy
    }

    private fun addVehicleToMap(vehicleList: MutableList<Marker>, mpkLine: String, googleMap: GoogleMap): MutableList<Marker> {
        val values = mpkLine.split(",")
        var delayMessage = " nie wiem ile :D"
        val transportMpkPosition = LatLng(values[4].toDouble(), values[5].toDouble())
        var vehicleNotAdded = true
        if (!values[8].equals("NP")) {
            delayMessage = " Opóźnienie:" + values[8] + "s"
        }
        if (vehicleList.isEmpty()) {
            val markerName: Marker = googleMap.addMarker(
                MarkerOptions()
                    .position(transportMpkPosition)
                    .title("Szczur - linia " + values[2])
                    .icon(BitmapDescriptorFactory.fromResource(R.drawable.mymarker))
                    .snippet("Kierunek: " + values[3] + delayMessage))
            markerName.tag = values[0]
            vehicleList.add(markerName)
        }
        for (marker in vehicleList) {
            if (marker.tag?.equals(values[0]) == true) {
                marker.setPosition(transportMpkPosition)
                marker.setSnippet("Kierunek: " + values[3] + delayMessage)
                vehicleNotAdded = false
                break
            }
        }
        if (vehicleNotAdded) {
            val markerName: Marker = googleMap.addMarker(
                MarkerOptions()
                    .position(transportMpkPosition)
                    .title("Szczur - linia " + values[2])
                    .icon(BitmapDescriptorFactory.fromResource(R.drawable.mymarker))
                    .snippet("Kierunek: " + values[3] + delayMessage))
            markerName.tag = values[0]
            vehicleList.add(markerName)
        }
        return vehicleList
    }
}