# ----------------------------------------------------------------------
# Fix GridFS no chunk #0
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.gridvcs.utils import REPOS
from noc.core.gridvcs.base import GridVCS


def fix():
    for repo in REPOS:
        fix_repo(repo)


def fix_repo(repo):
    vcs = GridVCS(repo)
    # Get files without chunk 0
    revs = {d["_id"] for d in vcs.fs._GridFS__files.find({}, {"_id": 1})}
    chunks = {d["files_id"] for d in vcs.fs._GridFS__chunks.find({"n": 0}, {"files_id": 1})}
    corrupt_files = revs - chunks
    if not corrupt_files:
        return
    # Reduce to corrupt objects
    corrupt_objects = {
        d["object"]
        for d in vcs.fs._GridFS__files.find(
            {"_id": {"$in": list(corrupt_files)}}, {"_id": 0, "object": 1}
        )
    }
    for obj in corrupt_objects:
        fix_object(vcs, obj, corrupt_files)


def fix_object(vcs, object, corrupt):
    print("@@@ %s" % object)
    revs = list(vcs.iter_revisions(object))
    show_revs(revs, corrupt)
    while True:
        cidx = find_corrupt(vcs, revs, corrupt)
        if cidx is None:
            break
        print("  -> CORRUPT %d" % cidx)
        cut_corrupt(vcs, revs, cidx)
        show_revs(revs, corrupt)


def find_corrupt(vcs, revs, corrupt):
    """
    Find first corrupt section and return its index
    :param vcs: GridVCS instance
    :param revs: List of Revision
    :param corrupt: Corrupted index (zero-based) or None if not corrupted
    :return:
    """
    for n, rev in enumerate(revs):
        if rev.id in corrupt:
            return n
    return None


def cut_corrupt(vcs, revs, cidx):
    """
    Cut corrupted part of the history
    :param vcs:
    :param revs:
    :param cidx:
    :return:
    """
    # Start of slice
    s = cidx
    while s > 0 and revs[s - 1].ft != "F":
        s -= 1
    # End of slice
    e = cidx + 1
    me = len(revs) - 1
    while e < me and revs[e].ft != "F":
        e += 1
    for rev in revs[s:e]:
        vcs.fs.delete(rev.id)
    del revs[s:e]


def show_revs(revs, corrupt):
    for r in revs:
        print("    %s %s %s" % (r.ts, r.ft, "*" if r.id in corrupt else " "))
