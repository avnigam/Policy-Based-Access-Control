class Version:
    object = None
    attribute = None
    attribute_value = None
    read_timestamp = None
    write_timestamp = None
    pendingMightRead = []
    pendingMightWrite = []

# Update the latest version into version DB
def update_latest_Version(data_versions, object, attributes, read_timestamp, write_timestamp):

    print("Attributes: " + str(attributes))
    i = 0
    for attribute in attributes:
        if i % 2 == 0:
            version_ack = None
            for version in data_versions:
                if version.object == object and version.attribute == attribute:
                    version_ack = version
                    break

            if version_ack:
                version_ack.write_timestamp = write_timestamp
                version_ack.read_timestamp = read_timestamp
                data_versions.remove(version_ack)
                data_versions.append(version_ack)
            else:
                ver = Version()
                ver.object = object
                ver.attribute = attribute
                # ver.value = attributes[i+1]
                ver.write_timestamp = write_timestamp
                ver.read_timestamp = read_timestamp
                ver.pendingMightRead = []
                ver.pendingMightWrite = []
                data_versions.append(ver)
                print("Len of data_version: " + str(len(data_versions)))

            i += 1

    return data_versions

# Get the Latest version before the timestamp specified
def latestVersionBefore(data_versions, object, attribute, timestamp):
    list_version = []
    for version in data_versions:
        if version.object == object and version.attribute == attribute:
            list_version.append(version)

    if list_version == []:
        ver = Version()
        ver.object = object
        ver.attribute = attribute
        ver.read_timestamp = 0
        ver.write_timestamp = 0
        return ver

    # Iterate through the list of version and return the first version with timestamp less than timestamp in the function parameter.
    for version in reversed(list_version):
        if version.write_timestamp < timestamp:
            return version

# Print the version object
def print_version(version):
    print("Version Object: " + str(version.object))
    print("Version Attribute: " + str(version.attribute))
    print("Version Read Timestamp: " + str(version.read_timestamp))
    print("Version Read Timestamp: " + str(version.write_timestamp))
