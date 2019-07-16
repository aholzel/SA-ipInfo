# Function to unzip .gz files
Function Unzip
{
	Param(
		$infile,
		$outfile = ($infile -replace '\.gz$','')
		)

	$input 			= New-Object System.IO.FileStream $inFile, ([IO.FileMode]::Open), ([IO.FileAccess]::Read), ([IO.FileShare]::Read)
	$output 		= New-Object System.IO.FileStream $outFile, ([IO.FileMode]::Create), ([IO.FileAccess]::Write), ([IO.FileShare]::None)
	$gzipStream 	= New-Object System.IO.Compression.GzipStream $input, ([IO.Compression.CompressionMode]::Decompress)

	$buffer 		= New-Object byte[](1024)
	while($true)
	{
		$read 		= $gzipstream.Read($buffer, 0, 1024)
		if ($read -le 0)
		{
			break
		}
		
		$output.Write($buffer, 0, $read)
	}

	$gzipStream.Close()
	$output.Close()
	$input.Close()
}

$currentDir 		= $PSScriptRoot 
$outputDir 			= Split-Path -Path $currentDir -Parent 

$downloadUrlFile	= "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"
$tempOutputFile 	= $outputDir + "\share\tmp\GeoLite2-City.mmdb.gz"
$OutputFile 		= $outputDir + "\share\GeoLite2-City.mmdb"

$downloadUrlMD5 	= "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.md5"
$newMD5File 		= $outputDir + "\share\tmp\GeoLite2-City-new.md5"
$currentMD5file 	= $outputDir + "\share\tmp\GeoLite2-City-current.md5"

#Download the new MD5 file
(New-Object System.Net.WebClient).DownloadFile($downloadUrlMD5, $newMD5File)

IF(Test-Path $newMD5File)
{
	$newMD5 		= [IO.File]::ReadAllText($newMD5File)
	$currentMD5		= [IO.File]::ReadAllText($currentMD5file)
	
	IF($newMD5 -ne $currentMD5)
	{
		# The MD5 hashes are not equal so download the new file
		(New-Object System.Net.WebClient).DownloadFile($downloadUrlFile, $tempOutputFile)
		# Copy the newMD5 file to be the current one
		Copy-Item $newMD5File $currentMD5file
		# Unzip the downloaded file
		Unzip $tempOutputFile $OutputFile
		# Remove the .gz file
		Remove-Item $tempOutputFile
	}
}
