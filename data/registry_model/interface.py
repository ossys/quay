from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class RegistryDataInterface(object):
    """
    Interface for code to work with the registry data model.

    The registry data model consists of all tables that store registry-specific information, such as
    Manifests, Blobs, Images, and Labels.
    """

    @abstractmethod
    def supports_schema2(self, namespace_name):
        """
        Returns whether the implementation of the data interface supports schema 2 format manifests.
        """

    @abstractmethod
    def get_tag_legacy_image_id(self, repository_ref, tag_name, storage):
        """
        Returns the legacy image ID for the tag with a legacy images in the repository.

        Returns None if None.
        """

    @abstractmethod
    def get_legacy_tags_map(self, repository_ref, storage):
        """
        Returns a map from tag name to its legacy image ID, for all tags with legacy images in the
        repository.

        Note that this can be a *very* heavy operation.
        """

    @abstractmethod
    def find_matching_tag(self, repository_ref, tag_names):
        """
        Finds an alive tag in the repository matching one of the given tag names and returns it or
        None if none.
        """

    @abstractmethod
    def get_most_recent_tag(self, repository_ref):
        """
        Returns the most recently pushed alive tag in the repository, if any.

        If none, returns None.
        """

    @abstractmethod
    def lookup_repository(self, namespace_name, repo_name, kind_filter=None):
        """
        Looks up and returns a reference to the repository with the given namespace and name, or
        None if none.
        """

    @abstractmethod
    def get_manifest_for_tag(self, tag, backfill_if_necessary=False, include_legacy_image=False):
        """
        Returns the manifest associated with the given tag.
        """

    @abstractmethod
    def lookup_manifest_by_digest(
        self,
        repository_ref,
        manifest_digest,
        allow_dead=False,
        include_legacy_image=False,
        require_available=False,
    ):
        """
        Looks up the manifest with the given digest under the given repository and returns it or
        None if none.

        If allow_dead is True, manifests pointed to by dead tags will also be returned. If
        require_available is True, a temporary tag will be added onto the returned manifest (before
        it is returned) to ensure it is available until another tagging or manifest operation is
        taken.
        """

    @abstractmethod
    def create_manifest_and_retarget_tag(
        self, repository_ref, manifest_interface_instance, tag_name, storage, raise_on_error=False
    ):
        """
        Creates a manifest in a repository, adding all of the necessary data in the model.

        The `manifest_interface_instance` parameter must be an instance of the manifest
        interface as returned by the image/docker package.

        Note that all blobs referenced by the manifest must exist under the repository or this
        method will fail and return None.

        Returns a reference to the (created manifest, tag) or (None, None) on error.
        """

    @abstractmethod
    def get_legacy_images(self, repository_ref):
        """
        Returns an iterator of all the LegacyImage's defined in the matching repository.
        """

    @abstractmethod
    def get_legacy_image(
        self, repository_ref, docker_image_id, include_parents=False, include_blob=False
    ):
        """
        Returns the matching LegacyImages under the matching repository, if any.

        If none, returns None.
        """

    @abstractmethod
    def create_manifest_label(self, manifest, key, value, source_type_name, media_type_name=None):
        """
        Creates a label on the manifest with the given key and value.

        Can raise InvalidLabelKeyException or InvalidMediaTypeException depending on the validation
        errors.
        """

    @abstractmethod
    def batch_create_manifest_labels(self, manifest):
        """
        Returns a context manager for batch creation of labels on a manifest.

        Can raise InvalidLabelKeyException or InvalidMediaTypeException depending on the validation
        errors.
        """

    @abstractmethod
    def list_manifest_labels(self, manifest, key_prefix=None):
        """
        Returns all labels found on the manifest.

        If specified, the key_prefix will filter the labels returned to those keys that start with
        the given prefix.
        """

    @abstractmethod
    def get_manifest_label(self, manifest, label_uuid):
        """
        Returns the label with the specified UUID on the manifest or None if none.
        """

    @abstractmethod
    def delete_manifest_label(self, manifest, label_uuid):
        """
        Delete the label with the specified UUID on the manifest.

        Returns the label deleted or None if none.
        """

    @abstractmethod
    def lookup_cached_active_repository_tags(
        self, model_cache, repository_ref, start_pagination_id, limit
    ):
        """
        Returns a page of active tags in a repository.

        Note that the tags returned by this method are ShallowTag objects, which only contain the
        tag name. This method will automatically cache the result and check the cache before making
        a call.
        """

    @abstractmethod
    def lookup_active_repository_tags(self, repository_ref, start_pagination_id, limit):
        """
        Returns a page of active tags in a repository.

        Note that the tags returned by this method are ShallowTag objects, which only contain the
        tag name.
        """

    @abstractmethod
    def list_all_active_repository_tags(self, repository_ref, include_legacy_images=False):
        """
        Returns a list of all the active tags in the repository.

        Note that this is a *HEAVY* operation on repositories with a lot of tags, and should only be
        used for testing or where other more specific operations are not possible.
        """

    @abstractmethod
    def list_repository_tag_history(
        self,
        repository_ref,
        page=1,
        size=100,
        specific_tag_name=None,
        active_tags_only=False,
        since_time_ms=None,
    ):
        """
        Returns the history of all tags in the repository (unless filtered).

        This includes tags that have been made in-active due to newer versions of those tags coming
        into service.
        """

    @abstractmethod
    def get_most_recent_tag_lifetime_start(self, repository_refs):
        """
        Returns a map from repository ID to the last modified time ( seconds from epoch, UTC) for
        each repository in the given repository reference list.
        """

    @abstractmethod
    def get_repo_tag(self, repository_ref, tag_name, include_legacy_image=False):
        """
        Returns the latest, *active* tag found in the repository, with the matching name or None if
        none.
        """

    @abstractmethod
    def has_expired_tag(self, repository_ref, tag_name):
        """
        Returns true if and only if the repository contains a tag with the given name that is
        expired.
        """

    @abstractmethod
    def retarget_tag(
        self,
        repository_ref,
        tag_name,
        manifest_or_legacy_image,
        storage,
        legacy_manifest_key,
        is_reversion=False,
    ):
        """
        Creates, updates or moves a tag to a new entry in history, pointing to the manifest or
        legacy image specified.

        If is_reversion is set to True, this operation is considered a reversion over a previous tag
        move operation. Returns the updated Tag or None on error.
        """

    @abstractmethod
    def delete_tag(self, repository_ref, tag_name):
        """
        Deletes the latest, *active* tag with the given name in the repository.
        """

    @abstractmethod
    def delete_tags_for_manifest(self, manifest):
        """
        Deletes all tags pointing to the given manifest, making the manifest inaccessible for
        pulling.

        Returns the tags deleted, if any. Returns None on error.
        """

    @abstractmethod
    def change_repository_tag_expiration(self, tag, expiration_date):
        """
        Sets the expiration date of the tag under the matching repository to that given.

        If the expiration date is None, then the tag will not expire. Returns a tuple of the
        previous expiration timestamp in seconds (if any), and whether the operation succeeded.
        """

    @abstractmethod
    def get_legacy_images_owned_by_tag(self, tag):
        """
        Returns all legacy images *solely owned and used* by the given tag.
        """

    @abstractmethod
    def get_security_status(self, manifest_or_legacy_image):
        """
        Returns the security status for the given manifest or legacy image or None if none.
        """

    @abstractmethod
    def reset_security_status(self, manifest_or_legacy_image):
        """
        Resets the security status for the given manifest or legacy image, ensuring that it will get
        re-indexed.
        """

    @abstractmethod
    def backfill_manifest_for_tag(self, tag):
        """
        Backfills a manifest for the V1 tag specified. If a manifest already exists for the tag,
        returns that manifest.

        NOTE: This method will only be necessary until we've completed the backfill, at which point
        it should be removed.
        """

    @abstractmethod
    def is_existing_disabled_namespace(self, namespace_name):
        """
        Returns whether the given namespace exists and is disabled.
        """

    @abstractmethod
    def is_namespace_enabled(self, namespace_name):
        """
        Returns whether the given namespace exists and is enabled.
        """

    @abstractmethod
    def get_manifest_local_blobs(self, manifest, include_placements=False):
        """
        Returns the set of local blobs for the given manifest or None if none.
        """

    @abstractmethod
    def list_manifest_layers(self, manifest, storage, include_placements=False):
        """
        Returns an *ordered list* of the layers found in the manifest, starting at the base and
        working towards the leaf, including the associated Blob and its placements (if specified).

        The layer information in `layer_info` will be of type
        `image.docker.types.ManifestImageLayer`. Should not be called for a manifest list.
        """

    @abstractmethod
    def list_parsed_manifest_layers(
        self, repository_ref, parsed_manifest, storage, include_placements=False
    ):
        """
        Returns an *ordered list* of the layers found in the parsed manifest, starting at the base
        and working towards the leaf, including the associated Blob and its placements (if
        specified).

        The layer information in `layer_info` will be of type
        `image.docker.types.ManifestImageLayer`. Should not be called for a manifest list.
        """

    @abstractmethod
    def lookup_derived_image(
        self, manifest, verb, storage, varying_metadata=None, include_placements=False
    ):
        """
        Looks up the derived image for the given manifest, verb and optional varying metadata and
        returns it or None if none.
        """

    @abstractmethod
    def lookup_or_create_derived_image(
        self,
        manifest,
        verb,
        storage_location,
        storage,
        varying_metadata=None,
        include_placements=False,
    ):
        """
        Looks up the derived image for the given maniest, verb and optional varying metadata and
        returns it.

        If none exists, a new derived image is created.
        """

    @abstractmethod
    def get_derived_image_signature(self, derived_image, signer_name):
        """
        Returns the signature associated with the derived image and a specific signer or None if
        none.
        """

    @abstractmethod
    def set_derived_image_signature(self, derived_image, signer_name, signature):
        """
        Sets the calculated signature for the given derived image and signer to that specified.
        """

    @abstractmethod
    def delete_derived_image(self, derived_image):
        """
        Deletes a derived image and all of its storage.
        """

    @abstractmethod
    def set_derived_image_size(self, derived_image, compressed_size):
        """
        Sets the compressed size on the given derived image.
        """

    @abstractmethod
    def get_torrent_info(self, blob):
        """
        Returns the torrent information associated with the given blob or None if none.
        """

    @abstractmethod
    def set_torrent_info(self, blob, piece_length, pieces):
        """
        Sets the torrent infomation associated with the given blob to that specified.
        """

    @abstractmethod
    def get_repo_blob_by_digest(self, repository_ref, blob_digest, include_placements=False):
        """
        Returns the blob in the repository with the given digest, if any or None if none.

        Note that there may be multiple records in the same repository for the same blob digest, so
        the return value of this function may change.
        """

    @abstractmethod
    def create_blob_upload(self, repository_ref, upload_id, location_name, storage_metadata):
        """
        Creates a new blob upload and returns a reference.

        If the blob upload could not be created, returns None.
        """

    @abstractmethod
    def lookup_blob_upload(self, repository_ref, blob_upload_id):
        """
        Looks up the blob upload with the given ID under the specified repository and returns it or
        None if none.
        """

    @abstractmethod
    def update_blob_upload(
        self,
        blob_upload,
        uncompressed_byte_count,
        piece_hashes,
        piece_sha_state,
        storage_metadata,
        byte_count,
        chunk_count,
        sha_state,
    ):
        """
        Updates the fields of the blob upload to match those given.

        Returns the updated blob upload or None if the record does not exists.
        """

    @abstractmethod
    def delete_blob_upload(self, blob_upload):
        """
        Deletes a blob upload record.
        """

    @abstractmethod
    def commit_blob_upload(self, blob_upload, blob_digest_str, blob_expiration_seconds):
        """
        Commits the blob upload into a blob and sets an expiration before that blob will be GCed.
        """

    @abstractmethod
    def mount_blob_into_repository(self, blob, target_repository_ref, expiration_sec):
        """
        Mounts the blob from another repository into the specified target repository, and adds an
        expiration before that blob is automatically GCed.

        This function is useful during push operations if an existing blob from another repository
        is being pushed. Returns False if the mounting fails. Note that this function does *not*
        check security for mounting the blob and the caller is responsible for doing this check (an
        example can be found in endpoints/v2/blob.py).
        """

    @abstractmethod
    def set_tags_expiration_for_manifest(self, manifest, expiration_sec):
        """
        Sets the expiration on all tags that point to the given manifest to that specified.
        """

    @abstractmethod
    def get_schema1_parsed_manifest(self, manifest, namespace_name, repo_name, tag_name, storage):
        """
        Returns the schema 1 version of this manifest, or None if none.
        """

    @abstractmethod
    def create_manifest_with_temp_tag(
        self, repository_ref, manifest_interface_instance, expiration_sec, storage
    ):
        """
        Creates a manifest under the repository and sets a temporary tag to point to it.

        Returns the manifest object created or None on error.
        """

    @abstractmethod
    def get_cached_namespace_region_blacklist(self, model_cache, namespace_name):
        """
        Returns a cached set of ISO country codes blacklisted for pulls for the namespace or None if
        the list could not be loaded.
        """

    @abstractmethod
    def convert_manifest(
        self, manifest, namespace_name, repo_name, tag_name, allowed_mediatypes, storage
    ):
        """
        Attempts to convert the specified into a parsed manifest with a media type in the
        allowed_mediatypes set.

        If not possible, or an error occurs, returns None.
        """

    @abstractmethod
    def yield_tags_for_vulnerability_notification(self, layer_id_pairs):
        """
        Yields tags that contain one (or more) of the given layer ID pairs, in repositories which
        have been registered for vulnerability_found notifications.

        Returns an iterator of LikelyVulnerableTag instances.
        """
