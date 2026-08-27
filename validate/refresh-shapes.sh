#!/bin/bash

GDBURL="https://cim.ontotext.com/graphdb/"
GDBUSER=""
GDBPASS=""

# Step 1: Download the ZIP file
curl -L https://github.com/ar-chad/application-profiles-library/archive/refs/heads/main.zip -o apl.zip || { echo "Failed to download ZIP file"; exit 1; }

# Step 2: Unzip the file
unzip -o apl.zip || { echo "Failed to unzip file"; exit 1; }

# Step 3: Navigate into the extracted directory
cd application-profiles-library-main/validate/ || { echo "Failed to enter the 'validate' directory"; exit 1; }

# Step 4: Run 'make zip' and 'make zip-rdfs' in the 'validate' directory
cp ../../Makefile .
make zip || { echo "Failed to execute 'make zip'"; exit 1; }
make zip-rdfs || { echo "Failed to execute 'make zip-rdfs'"; exit 1; }

# Step 5: Authenticate and extract the authorization token
GDB_AUTH_HEADER="X-GraphDB-Password: $GDBPASS"
GDB_AUTH_URL="$GDBURL""rest/login/""$GDBUSER"
auth_header=$(curl "$GDB_AUTH_URL" -X POST -H "$GDB_AUTH_HEADER" -I | grep "authorization:")
token=${auth_header#*: }
AUTH_HEADER="Authorization: Bearer $token"

# Step 6: Clean up the repository
curl  --http1.1 -H "$AUTH_HEADER" -X POST --data-urlencode "update@/drop.ru" "$GDBURL""repositories/cim-shacl/statements" || { echo "Failed to remove all data from $GDBURL repository"; exit 1; }

# Step 7: Upload shapes and rdfs to the repository
curl  --http1.1 -H "$AUTH_HEADER" -X POST --header 'Content-Type: application/zip' --data-binary @entsoe-SHACL.zip "$GDBURL""repositories/cim-shacl/statements?context=%3Chttps%3A%2F%2Fgithub.com%2Fentsoe%2Fapplication-profiles%2FSHACL%3E" || { echo "Failed to upload SHACL zip file to $GDBURL repository"; exit 1; }
curl  --http1.1 -H "$AUTH_HEADER" -X POST --header 'Content-Type: application/zip' --data-binary @entsoe-RDFS.zip "$GDBURL""repositories/cim-shacl/statements?context=%3Chttps%3A%2F%2Fgithub.com%2Fentsoe%2Fapplication-profiles%2FRDFS%3E" || { echo "Failed to upload RDFS zip file to $GDBURL repository"; exit 1; }

